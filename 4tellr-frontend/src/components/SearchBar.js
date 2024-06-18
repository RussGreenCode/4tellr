// src/components/SearchBar.js
import React, {useState} from 'react';
import { TextField, Box } from '@mui/material';
import '../styles/SearchBar.css';

const SearchBar = ({ setSearchEntry, label }) => {
  const [searchText, setSearchText] = useState('');

  const handleSearchChange = (event) => {
    const value = event.target.value;
    setSearchText(value);
    setSearchEntry({ eventKey: value });
  };

  return (
    <Box display="flex" justifyContent="center" className="search-bar">
      <TextField
        label={label}
        variant="outlined"
        size="small"
        value={searchText}
        onChange={handleSearchChange}
      />
    </Box>
  );
};

export default SearchBar;
