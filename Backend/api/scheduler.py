from datetime import datetime, timedelta

def calculate_revision_buffer(total_days):
    """
    Calculate the number of revision days.
    Default to ~15% of the total preparation time, bounded between 3 and 15 days.
    """
    if total_days <= 3:
        return 0
    elif total_days <= 10:
        return 2
    else:
        buffer_days = int(total_days * 0.15)
        return min(max(buffer_days, 3), 15)

def get_tasks_for_tier(tier, answer_format, topic_name, complexity):
    """
    Generate tailored, high-fidelity study tasks based on tier and answer format.
    """
    tasks = []
    
    if answer_format == 'MCQ':
        if tier == 'Baseline':
            tasks = [
                f"Study core concepts and formulas for {topic_name}.",
                f"Solve 10 practice MCQs (accuracy target: 70%).",
                "Review solutions for incorrect answers."
            ]
        elif tier == 'Plus5':
            tasks = [
                f"Deep dive into reference materials for {topic_name}.",
                f"Solve 20 medium-difficulty MCQs (accuracy target: 80%).",
                "Create a formula sheet / concept cheat sheet.",
                "Complete a quick weekly self-assessment quiz."
            ]
        else:  # Plus10
            tasks = [
                f"Exhaustive theoretical analysis of {topic_name}.",
                f"Solve 40 advanced-level MCQs (accuracy target: 90%).",
                "Analyze speed; target < 1.5 minutes per question.",
                "Practice negative marking simulation tests."
            ]
            
    elif answer_format == 'Descriptive':
        if tier == 'Baseline':
            tasks = [
                f"Read key texts and outline core arguments for {topic_name}.",
                "Draft one 250-word short answer question.",
                "Self-grade based on key textbook points."
            ]
        elif tier == 'Plus5':
            tasks = [
                f"Analyze standard sample essays / answers for {topic_name}.",
                "Write one 500-word essay under a 30-minute timer.",
                "Identify and memorize key quotes, stats, and definitions.",
                "Revise answer structure (Intro, Body, Conclusion)."
            ]
        else:  # Plus10
            tasks = [
                f"Perform critical literature/source review for {topic_name}.",
                "Write two comprehensive 800-word descriptive answers.",
                "Incorporate advanced academic vocabulary and diagram structures.",
                "Conduct self-evaluation against rigorous scoring rubrics."
            ]
            
    else:  # Practical, Oral, Other
        if tier == 'Baseline':
            tasks = [
                f"Review basic protocols and frequently asked questions for {topic_name}.",
                "Practice explaining the core concept aloud for 5 minutes."
            ]
        elif tier == 'Plus5':
            tasks = [
                f"Draft step-by-step practical setup guide for {topic_name}.",
                "Conduct a 15-minute mock verbal response recording.",
                "Review experimental errors or standard edge cases."
            ]
        else:  # Plus10
            tasks = [
                f"Conduct hands-on simulation or rigorous code run for {topic_name}.",
                "Perform a 30-minute mock panel interview with timer.",
                "Troubleshoot complex failure scenarios.",
                "Explain the topic to a non-technical peer (Feynman technique)."
            ]
            
    return tasks

def generate_plans(request_id, student_id, exam_category, answer_format, subject_name, exam_date_str, target_grade_percent, topics):
    """
    Derives Baseline, Target+5%, and Target+10% plans from a single list of weighted topics.
    Clamps target grade tiers at 100%.
    """
    exam_date = datetime.strptime(exam_date_str, "%Y-%m-%d").date()
    start_date = datetime.now().date()
    
    total_days = (exam_date - start_date).days
    if total_days < 1:
        total_days = 1 # Fallback for immediate exams
        
    revision_days = calculate_revision_buffer(total_days)
    study_days = max(1, total_days - revision_days)
    
    revision_start_date = start_date + timedelta(days=study_days)
    
    plans = []
    tiers = [
        ("Baseline", target_grade_percent),
        ("Plus5", min(target_grade_percent + 5, 100)),
        ("Plus10", min(target_grade_percent + 10, 100))
    ]
    
    for tier_name, tier_target in tiers:
        # Determine study hours based on target percentage
        # e.g., 75% -> 5 hours, 90% -> 6 hours
        base_hours = round(tier_target / 15.0, 1)
        daily_hours = min(max(base_hours, 2.0), 10.0)
        
        # Build the schedule array
        daily_schedule = []
        
        # Map topics to study days
        # We handle case where study_days >= len(topics) vs study_days < len(topics)
        if study_days >= len(topics):
            current_day = 0
            for i, topic in enumerate(topics):
                if i == len(topics) - 1:
                    num_days = study_days - current_day
                else:
                    num_days = max(1, round(topic["weight"] * study_days))
                    if current_day + num_days + (len(topics) - 1 - i) > study_days:
                        num_days = study_days - current_day - (len(topics) - 1 - i)
                        num_days = max(1, num_days)
                
                for d_offset in range(num_days):
                    if current_day < study_days:
                        day_date = start_date + timedelta(days=current_day)
                        
                        daily_schedule.append({
                            "day_number": current_day + 1,
                            "date": day_date.strftime("%Y-%m-%d"),
                            "is_revision": False,
                            "study_hours": daily_hours,
                            "topics": [{
                                "topic_id": topic["topic_id"],
                                "topic_name": topic["topic_name"],
                                "complexity": topic["complexity"],
                                "subtopics": topic["subtopics"],
                                "tasks": get_tasks_for_tier(tier_name, answer_format, topic["topic_name"], topic["complexity"])
                            }]
                        })
                        current_day += 1
        else:
            # Group topics for short timelines
            for d_idx in range(study_days):
                day_date = start_date + timedelta(days=d_idx)
                
                # Identify which topics belong to this day
                day_topics = []
                for i, topic in enumerate(topics):
                    assigned_day = int((i / len(topics)) * study_days)
                    assigned_day = min(assigned_day, study_days - 1)
                    if assigned_day == d_idx:
                        day_topics.append({
                            "topic_id": topic["topic_id"],
                            "topic_name": topic["topic_name"],
                            "complexity": topic["complexity"],
                            "subtopics": topic["subtopics"],
                            "tasks": get_tasks_for_tier(tier_name, answer_format, topic["topic_name"], topic["complexity"])
                        })
                
                daily_schedule.append({
                    "day_number": d_idx + 1,
                    "date": day_date.strftime("%Y-%m-%d"),
                    "is_revision": False,
                    "study_hours": daily_hours,
                    "topics": day_topics
                })
        
        # Append revision buffer days
        for r_idx in range(revision_days):
            day_num = study_days + r_idx + 1
            day_date = revision_start_date + timedelta(days=r_idx)
            
            # Formulate revision tasks
            if tier_name == 'Baseline':
                rev_tasks = [
                    "Revise all formula sheets, study guides, and notes.",
                    "Complete 1 full-length practice exam.",
                    "Review score and identify residual weak spots."
                ]
            elif tier_name == 'Plus5':
                rev_tasks = [
                    "Perform focused revision on previously identified weak topics.",
                    "Simulate 2 full-length practice exams under timing constraints.",
                    "Prepare cheat-sheets for last-minute recall."
                ]
            else: # Plus10
                rev_tasks = [
                    "Perform high-intensity active recall sessions.",
                    "Simulate 3 full-length practice exams during actual scheduled test hours.",
                    "Fine-tune pacing: resolve typical errors and optimize performance margins."
                ]
                
            daily_schedule.append({
                "day_number": day_num,
                "date": day_date.strftime("%Y-%m-%d"),
                "is_revision": True,
                "study_hours": daily_hours,
                "topics": [{
                    "topic_id": f"revision_{r_idx:02d}",
                    "topic_name": "Revision Window Phase",
                    "complexity": 5,
                    "subtopics": ["Comprehensive Review", "Mock Test Assessments"],
                    "tasks": rev_tasks
                }]
            })
            
        plans.append({
            "tier": tier_name,
            "target_grade_effective": tier_target,
            "daily_schedule_json": daily_schedule,
            "revision_start_date": revision_start_date.strftime("%Y-%m-%d"),
            "generated_at": datetime.now().isoformat()
        })
        
    return plans

def recompress_schedule(daily_schedule, completed_topic_ids, revision_start_date_str, current_date_str):
    """
    Pace adaptation engine:
    - Retains past completed topics in the days they were marked complete.
    - Gathers all incomplete topics.
    - Redistributes the incomplete topics across the study days remaining between today and revision_start_date.
    - Keeps the revision buffer intact.
    """
    today = datetime.strptime(current_date_str, "%Y-%m-%d").date()
    revision_start_date = datetime.strptime(revision_start_date_str, "%Y-%m-%d").date()
    
    # Separate past/completed history from future schedule
    history = []
    incomplete_topics = []
    
    # Parse existing schedule to extract all topics and check if they are incomplete
    for day in daily_schedule:
        day_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
        
        # If it's a revision day, keep it untouched
        if day["is_revision"]:
            continue
            
        if day_date < today:
            # Past days: keep as history
            history.append(day)
        else:
            # Present or Future study day: gather topics
            for topic in day["topics"]:
                # Check if this topic is completed
                if topic["topic_id"] not in completed_topic_ids:
                    # Deduplicate topics for redistribution
                    if topic["topic_id"] not in [t["topic_id"] for t in incomplete_topics]:
                        incomplete_topics.append(topic)
                        
    # If no topics are incomplete, no adjustment needed
    if not incomplete_topics:
        return daily_schedule, False
        
    # Calculate remaining study days before the revision window starts
    remaining_study_days = []
    curr = today
    while curr < revision_start_date:
        remaining_study_days.append(curr)
        curr += timedelta(days=1)
        
    # If no study days are left before revision, we must compress them into the revision window itself (edge case),
    # or treat today as the sole study day.
    if not remaining_study_days:
        remaining_study_days = [today]
        
    num_remaining_days = len(remaining_study_days)
    
    # Re-allocate incomplete topics across remaining study days
    new_study_schedule = []
    study_hours = daily_schedule[0]["study_hours"]  # Keep same study budget
    
    if num_remaining_days >= len(incomplete_topics):
        current_day_idx = 0
        topics_per_day = 1
        
        for i, topic in enumerate(incomplete_topics):
            # Compute days allocated based on relative size
            if i == len(incomplete_topics) - 1:
                days_alloc = num_remaining_days - current_day_idx
            else:
                days_alloc = max(1, round(num_remaining_days / len(incomplete_topics)))
                if current_day_idx + days_alloc + (len(incomplete_topics) - 1 - i) > num_remaining_days:
                    days_alloc = num_remaining_days - current_day_idx - (len(incomplete_topics) - 1 - i)
                    days_alloc = max(1, days_alloc)
                    
            for _ in range(days_alloc):
                if current_day_idx < num_remaining_days:
                    new_study_schedule.append({
                        "day_number": len(history) + current_day_idx + 1,
                        "date": remaining_study_days[current_day_idx].strftime("%Y-%m-%d"),
                        "is_revision": False,
                        "study_hours": study_hours,
                        "topics": [topic]
                    })
                    current_day_idx += 1
    else:
        # Group topics to pack them into fewer days
        for d_idx, day_date in enumerate(remaining_study_days):
            day_topics = []
            for i, topic in enumerate(incomplete_topics):
                assigned_day = int((i / len(incomplete_topics)) * num_remaining_days)
                assigned_day = min(assigned_day, num_remaining_days - 1)
                if assigned_day == d_idx:
                    day_topics.append(topic)
                    
            new_study_schedule.append({
                "day_number": len(history) + d_idx + 1,
                "date": day_date.strftime("%Y-%m-%d"),
                "is_revision": False,
                "study_hours": study_hours,
                "topics": day_topics
            })
            
    # Reconstruct the full schedule: History + New Study Days + Original Revision Days
    full_new_schedule = []
    full_new_schedule.extend(history)
    full_new_schedule.extend(new_study_schedule)
    
    # Copy revision days from the original schedule
    revision_days = [day for day in daily_schedule if day["is_revision"]]
    
    # Re-number revision days sequentially
    start_num = len(full_new_schedule) + 1
    for idx, rev_day in enumerate(revision_days):
        rev_day["day_number"] = start_num + idx
        full_new_schedule.append(rev_day)
        
    return full_new_schedule, True

def apply_feedback_patch(daily_schedule, feedback_text, adjustment_type, current_date_str):
    """
    Applies user feedback as a local patch.
    e.g., 'workload' -> reduce/increase hours.
    'pace' -> shift topics.
    Returns the modified schedule and description of the patch.
    """
    today = datetime.strptime(current_date_str, "%Y-%m-%d").date()
    modified = False
    details = ""
    
    if adjustment_type == "Workload":
        # Adjust study hours
        hours_delta = -1.0 if "reduce" in feedback_text.lower() or "less" in feedback_text.lower() else 1.0
        for day in daily_schedule:
            day_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
            if day_date >= today:
                day["study_hours"] = min(max(day["study_hours"] + hours_delta, 1.0), 12.0)
        modified = True
        details = f"Adjusted future daily study hours by {hours_delta:+.1f} hours."
        
    elif adjustment_type == "Pace":
        # Simulates shifting target topic priorities or dates.
        # We can append extra instructions to the current day tasks
        for day in daily_schedule:
            day_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
            if day_date >= today:
                for topic in day["topics"]:
                    if "tasks" in topic:
                        topic["tasks"].append("Adaptive Feedback: Modified task velocity to fit learner's pace preference.")
        modified = True
        details = "Injected custom pace adjustments into future tasks."
        
    else:
        # Standard fallback modification: insert instruction patch
        for day in daily_schedule:
            day_date = datetime.strptime(day["date"], "%Y-%m-%d").date()
            if day_date >= today:
                for topic in day["topics"]:
                    if "tasks" in topic:
                        topic["tasks"].append(f"Custom feedback adjustment: {feedback_text}")
        modified = True
        details = f"Applied custom patch details: {feedback_text}."
        
    return daily_schedule, modified, details
