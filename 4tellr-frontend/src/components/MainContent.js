// src/components/MainContent.js
import React from 'react';
import EventFetcher from './EventFetcher';
import '../styles/App.css';

const MainContent = ({businessDate}) => {
  return (
    <div className="main-content">
            <EventFetcher businessDate={businessDate} />
    </div>
  );
};

export default MainContent;
