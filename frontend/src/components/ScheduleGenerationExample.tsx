import React from 'react';
import { Card } from './Card';
import type { ScheduleGenerationRequest } from '../types/scheduleGeneration';

export const ScheduleGenerationExample: React.FC = () => {
  const exampleRequest: ScheduleGenerationRequest = {
    date: "2025-08-01",
    wakeUpTime: "07:00",
    activities: [
      { name: "Email review", durationMinutes: 30, priority: 2 },
      { name: "Team meeting", durationMinutes: 60, priority: 1, timeWindow: ["09:00", "11:00"] },
      { name: "Project work", durationMinutes: 180, priority: 3 },
      { name: "Gym", durationMinutes: 45, priority: 4 }
    ],
    constraints: {
      lunchBreak: true,
      maxConsecutiveWorkHours: 4
    }
  };

  return (
    <Card title="Example JSON Request" subtitle="This is the format sent to the backend">
      <pre className="bg-secondary-50 p-4 rounded-lg text-sm overflow-x-auto">
        <code>{JSON.stringify(exampleRequest, null, 2)}</code>
      </pre>
    </Card>
  );
};
