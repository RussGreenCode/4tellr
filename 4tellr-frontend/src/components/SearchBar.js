// src/components/SearchBar.js
import React, { useState } from 'react';
import { TextField, Box } from '@mui/material';
import '../styles/SearchBar.css';

const SearchBar = ({ setSearchEntry }) => {
  const [searchText, setSearchText] = useState('');

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setSearchText(value);
    setSearchEntry({ eventKey: value }); // Update search criteria with the eventKey
  };

  return (
    <Box display="flex" justifyContent="center" mt={2} mb={2}>
      <TextField
        label="Search"
        variant="outlined"
        size="small"
        value={searchText}
        onChange={handleSearchChange}
      />
    </Box>
  );
};

export default SearchBar;
