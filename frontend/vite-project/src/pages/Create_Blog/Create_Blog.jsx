import React, { useEffect, useState } from "react";
import "./Create_Blog.css";

function Create_Blog() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMSIsImV4cCI6MTc1Mzg5NzgwMn0.hC0lqS1eWmXqIrFcKRN7xFo1uqa4YCWSrpxFOzGg4TY"
    const channel = "create_blog";
    const eventSource = new EventSource(`http://localhost:8000/api/sse/events?channel=${channel}&token=${token}`);

    eventSource.onmessage = (event) => {
      setEvents((prevEvents) => [event.data, ...prevEvents]);
    };

    eventSource.onerror = () => {
      console.error("EventSource failed.");
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div className="container">
      <h1>📡 Live Updates</h1>
      <div className="event-list">
        {events.length === 0 && <p className="empty">Waiting for events...</p>}
        {events.map((event, index) => (
          <div className="event" key={index}>
            {event}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Create_Blog;
