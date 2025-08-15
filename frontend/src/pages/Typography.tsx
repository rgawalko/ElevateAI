import React from 'react';
import { Card, Button } from '../components';

export const Typography: React.FC = () => {
  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="heading-1 mb-4">Typography System</h1>
        <p className="body-text text-secondary-600">
          Showcasing the complete typography system with Inter, Montserrat, and Fira Code fonts.
        </p>
      </div>

      {/* Heading Scale */}
      <Card>
        <h2 className="heading-2 mb-6">Heading Scale (Montserrat)</h2>
        <div className="space-y-4">
          <div>
            <h1 className="heading-1">H1 - Main Page Title (48px/800)</h1>
            <p className="text-sm text-secondary-500 mt-1">heading-1 class</p>
          </div>
          <div>
            <h2 className="heading-2">H2 - Section Title (40px/700)</h2>
            <p className="text-sm text-secondary-500 mt-1">heading-2 class</p>
          </div>
          <div>
            <h3 className="heading-3">H3 - Subsection Title (32px/700)</h3>
            <p className="text-sm text-secondary-500 mt-1">heading-3 class</p>
          </div>
          <div>
            <h4 className="heading-4">H4 - Component Heading (28px/600)</h4>
            <p className="text-sm text-secondary-500 mt-1">heading-4 class</p>
          </div>
          <div>
            <h5 className="heading-5">H5 - Small Section (24px/600)</h5>
            <p className="text-sm text-secondary-500 mt-1">heading-5 class</p>
          </div>
          <div>
            <h6 className="heading-6">H6 - Smallest Heading (22px/600)</h6>
            <p className="text-sm text-secondary-500 mt-1">heading-6 class</p>
          </div>
        </div>
      </Card>

      {/* Body Text */}
      <Card>
        <h2 className="heading-2 mb-6">Body Text (Inter)</h2>
        <div className="space-y-4">
          <div>
            <p className="body-text">
              This is regular body text using Inter at 16px with 400 weight and 1.6 line height. 
              It's designed for optimal readability and comfortable reading experience across all devices.
            </p>
            <p className="text-sm text-secondary-500 mt-1">body-text class (400 weight)</p>
          </div>
          <div>
            <p className="body-text-medium">
              This is medium weight body text using Inter at 16px with 500 weight. 
              It provides subtle emphasis while maintaining excellent readability.
            </p>
            <p className="text-sm text-secondary-500 mt-1">body-text-medium class (500 weight)</p>
          </div>
          <div>
            <p className="body-text-semibold">
              This is semibold body text using Inter at 16px with 600 weight. 
              Perfect for labels, important content, and UI elements that need emphasis.
            </p>
            <p className="text-sm text-secondary-500 mt-1">body-text-semibold class (600 weight)</p>
          </div>
        </div>
      </Card>

      {/* Code Text */}
      <Card>
        <h2 className="heading-2 mb-6">Code Text (Fira Code)</h2>
        <div className="space-y-4">
          <div>
            <p className="body-text mb-2">
              Inline code example: <code className="code-text">const greeting = "Hello World!";</code>
            </p>
            <p className="text-sm text-secondary-500">code-text class for inline code</p>
          </div>
          <div>
            <p className="body-text mb-2">Code block example:</p>
            <pre className="code-block">
{`function calculateTotal(items) {
  return items.reduce((sum, item) => {
    return sum + (item.price * item.quantity);
  }, 0);
}

// Arrow function with ligatures
const multiply = (a, b) => a * b;
const isEqual = (x, y) => x === y;`}
            </pre>
            <p className="text-sm text-secondary-500 mt-2">code-block class with ligatures enabled</p>
          </div>
        </div>
      </Card>

      {/* UI Components */}
      <Card>
        <h2 className="heading-2 mb-6">UI Components</h2>
        <div className="space-y-6">
          <div>
            <h3 className="heading-4 mb-3">Buttons (Inter 600)</h3>
            <div className="flex flex-wrap gap-3">
              <Button variant="primary">Primary Button</Button>
              <Button variant="secondary">Secondary Button</Button>
              <Button variant="accent">Accent Button</Button>
              <Button variant="outline">Outline Button</Button>
            </div>
          </div>
          
          <div>
            <h3 className="heading-4 mb-3">Form Elements (Inter 400)</h3>
            <div className="space-y-3 max-w-md">
              <input 
                className="input" 
                placeholder="Input field with Inter 16px/1.6" 
                defaultValue="Sample text input"
              />
              <textarea 
                className="input min-h-[100px] resize-none" 
                placeholder="Textarea with consistent typography"
                defaultValue="This textarea uses the same typography system as other form elements."
              />
            </div>
          </div>
        </div>
      </Card>

      {/* Typography Hierarchy */}
      <Card>
        <h2 className="heading-2 mb-6">Typography Hierarchy Example</h2>
        <article className="prose prose-lg max-w-none">
          <h1 className="heading-1">The Future of Productivity</h1>
          <p className="body-text text-secondary-600 text-lg mb-6">
            How AI-powered tools are revolutionizing the way we work and live.
          </p>
          
          <h2 className="heading-2 mt-8 mb-4">Understanding Modern Workflows</h2>
          <p className="body-text mb-4">
            In today's fast-paced digital environment, productivity isn't just about doing more—it's about 
            doing the right things efficiently. The integration of artificial intelligence into our daily 
            workflows represents a fundamental shift in how we approach tasks and time management.
          </p>
          
          <h3 className="heading-3 mt-6 mb-3">Key Benefits</h3>
          <p className="body-text mb-3">
            Modern productivity tools offer several advantages:
          </p>
          <ul className="body-text space-y-2 ml-6">
            <li>Intelligent task prioritization</li>
            <li>Automated scheduling optimization</li>
            <li>Real-time performance insights</li>
          </ul>
          
          <h4 className="heading-4 mt-6 mb-3">Implementation Example</h4>
          <p className="body-text mb-3">
            Here's how you might implement a simple task scheduler:
          </p>
          <pre className="code-block">
{`// Task scheduler with priority queue
class TaskScheduler {
  constructor() {
    this.tasks = [];
  }
  
  addTask(task, priority = 1) {
    this.tasks.push({ task, priority, timestamp: Date.now() });
    this.tasks.sort((a, b) => b.priority - a.priority);
  }
  
  getNextTask() {
    return this.tasks.shift();
  }
}`}
          </pre>
        </article>
      </Card>
    </div>
  );
};
