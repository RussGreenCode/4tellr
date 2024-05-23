// src/components/useDemoConfig.js
import { useState } from 'react';

const generateRandomData = (series, dataType, useR) => {
  return Array(series)
    .fill(0)
    .map((_, index) => ({
      label: `Series ${index + 1}`,
      data: Array(50)
        .fill(0)
        .map((_, index) => ({
          primary: new Date().getTime() + index * 3600000,
          secondary: Math.random() * 100,
          radius: useR ? Math.random() * 30 : 5,
        })),
    }));
};

export default function useDemoConfig({ series = 10, dataType = 'linear', useR = false }) {
  const [data, setData] = useState(generateRandomData(series, dataType, useR));

  const randomizeData = () => {
    setData(generateRandomData(series, dataType, useR));
  };

  return { data, randomizeData };
}
