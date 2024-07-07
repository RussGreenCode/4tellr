// src/components/FilteredSearchBar.js
import React, { useState, useEffect } from 'react';
import { TextField, List, ListItem, ListItemText, Box, Paper } from '@mui/material';
import '../styles/FilteredSearchBar.css';

const FilteredSearchBar = ({ label, setSearchEntry, options }) => {
  const [searchText, setSearchText] = useState('');
  const [filteredOptions, setFilteredOptions] = useState([]);

  useEffect(() => {
    if (searchText.length >= 3) {
      const filtered = options.filter(option =>
        option.toLowerCase().includes(searchText.toLowerCase())
      );
      setFilteredOptions(filtered);
    } else {
      setFilteredOptions([]);
    }
  }, [searchText, options]);

  const handleInputChange = (e) => {
    setSearchText(e.target.value);
    setSearchEntry({ 'groupName': e.target.value });
  };


  const handleOptionClick = (option) => {
    setSearchText(option);
    setSearchEntry({ 'groupName': option });
    setFilteredOptions([]); // Clear the filtered options to hide the dropdown
  };

  return (
    <Box position="relative">
      <TextField
        label={label}
        variant="outlined"
        fullWidth
        value={searchText}
        onChange={handleInputChange}
        onBlur={() => setTimeout(() => setFilteredOptions([]), 100)} // Hide options when focus is lost
      />
      {filteredOptions.length > 0 && (
        <Paper elevation={3} style={{ position: 'absolute', width: '100%', zIndex: 1, backgroundColor: 'white', borderRadius: '4px', marginTop: '4px' }}>
          <List>
            {filteredOptions.map((option, index) => (
              <ListItem button key={index} onMouseDown={() => handleOptionClick(option)}>
                <ListItemText primary={option} />
              </ListItem>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
};

export default FilteredSearchBar;
