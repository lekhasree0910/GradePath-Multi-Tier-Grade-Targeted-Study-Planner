from django.test import TestCase, Client
from django.urls import reverse
from api.models import db_users, db_courses
from django.conf import settings
import json
import os

class GradePathApiTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Track inserted emails and courses to clean up
        self.test_emails = []
        self.test_course_ids = []

    def tearDown(self):
        # Clean up test documents in MongoDB to keep it pristine
        if self.test_emails:
            db_users.delete_many({"email": {"$in": self.test_emails}})
            settings.MONGO_DB["sessions"].delete_many({"email": {"$in": self.test_emails}})
        if self.test_course_ids:
            db_courses.delete_many({"course_id": {"$in": self.test_course_ids}})

    def test_student_registration_and_login(self):
        # 1. Register a student successfully
        reg_payload = {
            "full_name": "Test Student",
            "email": "teststudent@example.com",
            "password": "password123",
            "role": "Student"
        }
        self.test_emails.append(reg_payload["email"])
        response = self.client.post(
            reverse("auth_register"),
            data=json.dumps(reg_payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertTrue(data.get("success"))
        self.assertIn("user_id", data)

        # 2. Login as the student
        login_payload = {
            "email": "teststudent@example.com",
            "password": "password123",
            "role": "Student"
        }
        response = self.client.post(
            reverse("auth_login"),
            data=json.dumps(login_payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("token", data)
        self.assertEqual(data.get("full_name"), "Test Student")
        self.assertEqual(data.get("role"), "Student")

    def test_registration_validation(self):
        # Short password
        reg_payload = {
            "full_name": "Test Student Short",
            "email": "teststudent_short@example.com",
            "password": "123",
            "role": "Student"
        }
        self.test_emails.append(reg_payload["email"])
        response = self.client.post(
            reverse("auth_register"),
            data=json.dumps(reg_payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_admin_registration_with_secret(self):
        # Register admin with incorrect secret
        reg_payload = {
            "full_name": "Test Admin Fail",
            "email": "testadminfail@example.com",
            "password": "password123",
            "role": "Admin",
            "admin_secret": "WRONG_SECRET"
        }
        self.test_emails.append(reg_payload["email"])
        response = self.client.post(
            reverse("auth_register"),
            data=json.dumps(reg_payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 403)
        self.assertIn("error", response.json())

        # Register admin with correct secret
        reg_payload["admin_secret"] = "GRADEPATH_ADMIN_2024"
        reg_payload["email"] = "testadminpass@example.com"
        self.test_emails.append(reg_payload["email"])
        response = self.client.post(
            reverse("auth_register"),
            data=json.dumps(reg_payload),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(response.json().get("success"))

    def test_courses_listing(self):
        response = self.client.get(reverse("courses_list"))
        self.assertEqual(response.status_code, 200)
        courses = response.json()
        self.assertIsInstance(courses, list)

    def test_ai_engine_syllabus_analysis(self):
        """Test that the AI engine can analyze syllabus text"""
        from api.ai_engine import analyze_syllabus
        
        # Test syllabus text
        syllabus_text = """
        1. Mechanics
           - Kinematics
           - Newton's Laws
           - Work and Energy
        2. Electricity and Magnetism
           - Coulomb's Law
           - Electric Fields
           - Magnetic Fields
        3. Waves and Optics
           - Wave Properties
           - Sound Waves
           - Light and Optics
        """
        
        # Test with different exam categories and answer formats
        test_cases = [
            ("Competitive", "MCQ"),
            ("Academic", "Descriptive"),
            ("Vocational", "Practical")
        ]
        
        for exam_category, answer_format in test_cases:
            with self.subTest(exam_category=exam_category, answer_format=answer_format):
                # This should work without throwing an exception
                topics = analyze_syllabus(syllabus_text, exam_category, answer_format)
                
                # Basic validations
                self.assertIsInstance(topics, list)
                self.assertGreater(len(topics), 0)
                
                # Check that each topic has the required fields
                for topic in topics:
                    self.assertIn("topic_id", topic)
                    self.assertIn("topic_name", topic)
                    self.assertIn("subtopics", topic)
                    self.assertIn("complexity", topic)
                    self.assertIn("weight", topic)
                    
                    # Validate data types and ranges
                    self.assertIsInstance(topic["topic_id"], str)
                    self.assertIsInstance(topic["topic_name"], str)
                    self.assertIsInstance(topic["subtopics"], list)
                    self.assertGreaterEqual(topic["complexity"], 1)
                    self.assertLessEqual(topic["complexity"], 5)
                    self.assertGreaterEqual(topic["weight"], 0)
                    self.assertLessEqual(topic["weight"], 1)
                    
                # Verify that weights sum to approximately 1.0
                total_weight = sum(topic["weight"] for topic in topics)
                self.assertAlmostEqual(total_weight, 1.0, places=1)
                
    def test_ai_engine_fallback_behavior(self):
        """Test that the AI engine properly falls back to simulation when API is not configured"""
        from api.ai_engine import _analyze_syllabus_simulation, analyze_syllabus
        from unittest.mock import patch
        
        syllabus_text = "Introduction to Physics\nNewton's Laws\nEnergy Conservation"
        
        # Test the direct simulation function
        topics = _analyze_syllabus_simulation(syllabus_text, "Competitive", "MCQ")
        self.assertIsInstance(topics, list)
        self.assertGreater(len(topics), 0)
        
        # Test that the main function works (will use simulation since no valid API key)
        with patch.dict(os.environ, {'GROK_API_KEY': 'your_grok_api_key_here'}):
            topics = analyze_syllabus(syllabus_text, "Competitive", "MCQ")
            self.assertIsInstance(topics, list)
            self.assertGreater(len(topics), 0)
