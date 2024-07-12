// src/utils/ExportUtils.js

import { saveAs } from 'file-saver';
import Papa from 'papaparse';

export const exportToCSV = (data, filename) => {
  try {
    const csv = Papa.unparse(data);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    saveAs(blob, filename);
  } catch (err) {
    console.error('Error exporting to CSV:', err);
  }
};
