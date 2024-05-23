// src/components/ChartComponent.js
import React from 'react';
import { AxisOptions, Chart } from 'react-charts';
import ResizableBox from './ResizableBox';
import useDemoConfig from './UseDemoConfig';
import '../styles/App.css';

const ChartComponent = () => {
  const { data, randomizeData } = useDemoConfig({
    series: 3,
    dataType: 'linear',
    useR: false,
  });

  const primaryAxis = React.useMemo(() => ({
    getValue: (datum) => datum.primary,
  }), [data]);

  const secondaryAxes = React.useMemo(() => [
    {
      getValue: (datum) => datum.secondary,
      elementType: 'bubble',
    },
  ], [data]);

  return (
    <>
      <button onClick={randomizeData}>Randomize Data</button>
      <br />
      <br />
      <ResizableBox>
        <Chart
          options={{
            data,
            primaryAxis,
            secondaryAxes,
            interactionMode: 'closest',
            getDatumStyle: (datum) => ({
              circle: { r: datum.originalDatum.radius },
            }),
          }}
        />
      </ResizableBox>
    </>
  );
};

export default ChartComponent;
