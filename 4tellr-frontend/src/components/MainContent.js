// src/components/MainContent.js
import React from 'react';
import EventFetcher from './EventFetcher';
import '../styles/App.css';

const MainContent = ({businessDate}) => {
  return (
    <div className="main-content">
            <EventFetcher />
    </div>
  );
};

export default MainContent;
