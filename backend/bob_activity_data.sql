-- SQL script to populate Bob Chen with activity data for demonstration
-- Bob Chen's user ID: 5c773246-f9d3-48cf-b6d7-889111c6da2a

-- Clear existing activity logs for Bob Chen (optional)
-- DELETE FROM activity_logs WHERE user_id = '5c773246-f9d3-48cf-b6d7-889111c6da2a';

-- Insert activity data for the past 10 days
-- Day 1 (today)
INSERT INTO activity_logs (id, user_id, date, activities, notes, created_at) VALUES (
    gen_random_uuid(),
    '5c773246-f9d3-48cf-b6d7-889111c6da2a',
    CURRENT_DATE,
    '[
        {"name": "Feature Development", "category": "coding", "duration": 120, "productivity": 8, "mood": 7, "energy": 8, "notes": "Worked on user authentication feature"},
        {"name": "Code Review", "category": "review", "duration": 45, "productivity": 7, "mood": 6, "energy": 7, "notes": "Reviewed pull requests from team"},
        {"name": "Team Meeting", "category": "meeting", "duration": 60, "productivity": 6, "mood": 6, "energy": 6, "notes": "Sprint planning session"},
        {"name": "Learning/Training", "category": "learning", "duration": 90, "productivity": 9, "mood": 8, "energy": 8, "notes": "Studied React advanced patterns"}
    ]'::jsonb,
    'Daily activities - 4 activities completed',
    NOW()
);

-- Day 2 (yesterday)
INSERT INTO activity_logs (id, user_id, date, activities, notes, created_at) VALUES (
    gen_random_uuid(),
    '5c773246-f9d3-48cf-b6d7-889111c6da2a',
    CURRENT_DATE - INTERVAL '1 day',
    '[
        {"name": "Bug Fixing", "category": "debugging", "duration": 90, "productivity": 6, "mood": 5, "energy": 6, "notes": "Fixed critical authentication bug"},
        {"name": "System Design", "category": "design", "duration": 120, "productivity": 8, "mood": 7, "energy": 7, "notes": "Designed new API architecture"},
        {"name": "Documentation", "category": "documentation", "duration": 60, "productivity": 7, "mood": 6, "energy": 6, "notes": "Updated API documentation"},
        {"name": "Email Processing", "category": "communication", "duration": 30, "productivity": 5, "mood": 5, "energy": 5, "notes": "Processed daily emails"}
    ]'::jsonb,
    'Daily activities - 4 activities completed',
    NOW()
);

-- Day 3
INSERT INTO activity_logs (id, user_id, date, activities, notes, created_at) VALUES (
    gen_random_uuid(),
    '5c773246-f9d3-48cf-b6d7-889111c6da2a',
    CURRENT_DATE - INTERVAL '2 days',
    '[
        {"name": "Feature Development", "category": "coding", "duration": 150, "productivity": 9, "mood": 8, "energy": 8, "notes": "Implemented payment integration"},
        {"name": "Testing", "category": "testing", "duration": 75, "productivity": 7, "mood": 6, "energy": 6, "notes": "Wrote unit tests for new features"},
        {"name": "Sprint Planning", "category": "planning", "duration": 90, "productivity": 7, "mood": 6, "energy": 6, "notes": "Planned next sprint tasks"},
        {"name": "Code Review", "category": "review", "duration": 45, "productivity": 8, "mood": 7, "energy": 7, "notes": "Reviewed team code submissions"}
    ]'::jsonb,
    'Daily activities - 4 activities completed',
    NOW()
);

-- Day 4
INSERT INTO activity_logs (id, user_id, date, activities, notes, created_at) VALUES (
    gen_random_uuid(),
    '5c773246-f9d3-48cf-b6d7-889111c6da2a',
    CURRENT_DATE - INTERVAL '3 days',
    '[
        {"name": "Learning/Training", "category": "learning", "duration": 120, "productivity": 9, "mood": 9, "energy": 8, "notes": "Completed TypeScript advanced course"},
        {"name": "Feature Development", "category": "coding", "duration": 105, "productivity": 8, "mood": 7, "energy": 7, "notes": "Built dashboard components"},
        {"name": "Team Meeting", "category": "meeting", "duration": 45, "productivity": 6, "mood": 6, "energy": 6, "notes": "Weekly team sync"},
        {"name": "Documentation", "category": "documentation", "duration": 60, "productivity": 7, "mood": 6, "energy": 6, "notes": "Updated project README"}
    ]'::jsonb,
    'Daily activities - 4 activities completed',
    NOW()
);

-- Day 5
INSERT INTO activity_logs (id, user_id, date, activities, notes, created_at) VALUES (
    gen_random_uuid(),
    '5c773246-f9d3-48cf-b6d7-889111c6da2a',
    CURRENT_DATE - INTERVAL '4 days',
    '[
        {"name": "Bug Fixing", "category": "debugging", "duration": 75, "productivity": 7, "mood": 6, "energy": 6, "notes": "Resolved performance issues"},
        {"name": "System Design", "category": "design", "duration": 135, "productivity": 8, "mood": 7, "energy": 7, "notes": "Designed microservices architecture"},
        {"name": "Code Review", "category": "review", "duration": 60, "productivity": 7, "mood": 6, "energy": 7, "notes": "Reviewed security implementations"},
        {"name": "Email Processing", "category": "communication", "duration": 25, "productivity": 5, "mood": 5, "energy": 5, "notes": "Daily email management"}
    ]'::jsonb,
    'Daily activities - 4 activities completed',
    NOW()
);

-- Day 6
INSERT INTO activity_logs (id, user_id, date, activities, notes, created_at) VALUES (
    gen_random_uuid(),
    '5c773246-f9d3-48cf-b6d7-889111c6da2a',
    CURRENT_DATE - INTERVAL '5 days',
    '[
        {"name": "Feature Development", "category": "coding", "duration": 180, "productivity": 9, "mood": 8, "energy": 8, "notes": "Completed user profile feature"},
        {"name": "Testing", "category": "testing", "duration": 90, "productivity": 8, "mood": 7, "energy": 7, "notes": "Integration testing for new features"},
        {"name": "Learning/Training", "category": "learning", "duration": 75, "productivity": 9, "mood": 8, "energy": 8, "notes": "Studied cloud architecture patterns"},
        {"name": "Sprint Planning", "category": "planning", "duration": 60, "productivity": 7, "mood": 6, "energy": 6, "notes": "Sprint retrospective and planning"}
    ]'::jsonb,
    'Daily activities - 4 activities completed',
    NOW()
);

-- Day 7
INSERT INTO activity_logs (id, user_id, date, activities, notes, created_at) VALUES (
    gen_random_uuid(),
    '5c773246-f9d3-48cf-b6d7-889111c6da2a',
    CURRENT_DATE - INTERVAL '6 days',
    '[
        {"name": "Code Review", "category": "review", "duration": 50, "productivity": 8, "mood": 7, "energy": 7, "notes": "Reviewed critical bug fixes"},
        {"name": "Feature Development", "category": "coding", "duration": 140, "productivity": 8, "mood": 7, "energy": 7, "notes": "Implemented search functionality"},
        {"name": "Team Meeting", "category": "meeting", "duration": 75, "productivity": 6, "mood": 6, "energy": 6, "notes": "Architecture review meeting"},
        {"name": "Documentation", "category": "documentation", "duration": 45, "productivity": 7, "mood": 6, "energy": 6, "notes": "Updated technical specifications"}
    ]'::jsonb,
    'Daily activities - 4 activities completed',
    NOW()
);

-- Day 8
INSERT INTO activity_logs (id, user_id, date, activities, notes, created_at) VALUES (
    gen_random_uuid(),
    '5c773246-f9d3-48cf-b6d7-889111c6da2a',
    CURRENT_DATE - INTERVAL '7 days',
    '[
        {"name": "Learning/Training", "category": "learning", "duration": 105, "productivity": 9, "mood": 9, "energy": 8, "notes": "Learned about GraphQL best practices"},
        {"name": "Bug Fixing", "category": "debugging", "duration": 85, "productivity": 7, "mood": 6, "energy": 6, "notes": "Fixed database connection issues"},
        {"name": "System Design", "category": "design", "duration": 110, "productivity": 8, "mood": 7, "energy": 7, "notes": "Designed caching strategy"},
        {"name": "Email Processing", "category": "communication", "duration": 35, "productivity": 5, "mood": 5, "energy": 5, "notes": "Weekly email cleanup"}
    ]'::jsonb,
    'Daily activities - 4 activities completed',
    NOW()
);

-- Day 9
INSERT INTO activity_logs (id, user_id, date, activities, notes, created_at) VALUES (
    gen_random_uuid(),
    '5c773246-f9d3-48cf-b6d7-889111c6da2a',
    CURRENT_DATE - INTERVAL '8 days',
    '[
        {"name": "Feature Development", "category": "coding", "duration": 165, "productivity": 8, "mood": 7, "energy": 7, "notes": "Built notification system"},
        {"name": "Testing", "category": "testing", "duration": 70, "productivity": 7, "mood": 6, "energy": 6, "notes": "End-to-end testing"},
        {"name": "Code Review", "category": "review", "duration": 40, "productivity": 7, "mood": 6, "energy": 7, "notes": "Reviewed frontend components"},
        {"name": "Sprint Planning", "category": "planning", "duration": 80, "productivity": 7, "mood": 6, "energy": 6, "notes": "Sprint planning and estimation"}
    ]'::jsonb,
    'Daily activities - 4 activities completed',
    NOW()
);

-- Day 10
INSERT INTO activity_logs (id, user_id, date, activities, notes, created_at) VALUES (
    gen_random_uuid(),
    '5c773246-f9d3-48cf-b6d7-889111c6da2a',
    CURRENT_DATE - INTERVAL '9 days',
    '[
        {"name": "System Design", "category": "design", "duration": 125, "productivity": 8, "mood": 7, "energy": 7, "notes": "Designed real-time messaging system"},
        {"name": "Learning/Training", "category": "learning", "duration": 95, "productivity": 9, "mood": 8, "energy": 8, "notes": "Studied WebSocket implementation"},
        {"name": "Bug Fixing", "category": "debugging", "duration": 65, "productivity": 6, "mood": 5, "energy": 6, "notes": "Fixed memory leak issues"},
        {"name": "Documentation", "category": "documentation", "duration": 55, "productivity": 7, "mood": 6, "energy": 6, "notes": "Created deployment guide"}
    ]'::jsonb,
    'Daily activities - 4 activities completed',
    NOW()
);

-- Verify the data was inserted
SELECT 
    date,
    jsonb_array_length(activities) as activity_count,
    notes
FROM activity_logs 
WHERE user_id = '5c773246-f9d3-48cf-b6d7-889111c6da2a'
ORDER BY date DESC
LIMIT 10;
