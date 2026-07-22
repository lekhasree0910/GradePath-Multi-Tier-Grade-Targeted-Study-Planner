from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path('auth/register/', views.auth_register, name='auth_register'),
    path('auth/login/', views.auth_login, name='auth_login'),
    path('auth/logout/', views.auth_logout, name='auth_logout'),
    path('users/<int:user_id>/profile/', views.user_profile, name='user_profile'),

    # Roadmap Courses
    path('courses/', views.courses_list, name='courses_list'),
    path('courses/<int:course_id>/', views.course_detail, name='course_detail'),

    # Syllabus Intake & Bank
    path('syllabus-bank/', views.syllabus_bank_list, name='syllabus_bank_list'),
    path('syllabus/upload/', views.syllabus_upload, name='syllabus_upload'),

    # Customization & Scheduling
    path('plans/customize/', views.customize_plan_submit, name='customize_plan_submit'),
    path('plans/request/<int:request_id>/', views.get_plans_by_request, name='get_plans_by_request'),
    path('plans/<int:plan_id>/', views.plan_detail, name='plan_detail'),

    # Progress Tracking & Recompression
    path('plans/<int:plan_id>/progress/', views.plan_progress, name='plan_progress'),
    path('plans/<int:plan_id>/recompress/', views.plan_recompress, name='plan_recompress'),

    # Feedback Subsystem
    path('plans/<int:plan_id>/feedback/', views.plan_feedback_submit, name='plan_feedback_submit'),
    path('plans/<int:plan_id>/versions/', views.plan_version_history, name='plan_version_history'),

    # Vault
    path('vault/<int:student_id>/', views.vault_list, name='vault_list'),
    path('vault/session/<int:vault_id>/', views.vault_detail, name='vault_detail_get'),
    path('vault/session/<int:vault_id>/reopen/', views.vault_reopen, name='vault_reopen'),
    # Note: DELETE method is also handled at vault/session/<int:vault_id>/ endpoint

    # Admin Analytics
    path('admin/analytics/usage/', views.admin_usage_metrics, name='admin_usage_metrics'),
    path('admin/analytics/difficulty-trends/', views.admin_difficulty_trends, name='admin_difficulty_trends'),
    path('admin/students/', views.admin_students_list, name='admin_students_list'),

    # Admin Registration Requests
    path('auth/admin-request/', views.admin_request_create, name='admin_request_create'),
    path('admin/requests/', views.admin_requests_list, name='admin_requests_list'),
    path('admin/requests/<int:request_id>/action/', views.admin_request_action, name='admin_request_action'),
    path("chat/", views.chat_view, name="chat"),
]
