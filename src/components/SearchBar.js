// src/components/SearchBar.js
import React from 'react';
import { TextField, Box } from '@mui/material';
import '../styles/SearchBar.css';

const SearchBar = () => (
  <Box display="flex" justifyContent="center" mt={2} mb={2}>
    <TextField label="Search" variant="outlined" size="small" />
  </Box>
);

export default SearchBar;
