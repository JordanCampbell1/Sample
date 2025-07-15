// src/App.jsx
import React, { useEffect, useState } from "react";
import "./App.css";

function App() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const eventSource = new EventSource("http://localhost:8000/api/sse/events");

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

export default App;
