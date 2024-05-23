// src/components/ResizableBox.js
import React from 'react';
import { useState, useEffect } from 'react';

export default function ResizableBox({ children }) {
  const [width, setWidth] = useState(window.innerWidth);
  const [height, setHeight] = useState(window.innerHeight);

  useEffect(() => {
    const handleResize = () => {
      setWidth(window.innerWidth);
      setHeight(window.innerHeight);
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return (
    <div
      style={{
        width: width * 0.8,
        height: height * 0.6,
        resize: 'both',
        overflow: 'hidden',
        border: '1px solid black',
      }}
    >
      {children}
    </div>
  );
}
