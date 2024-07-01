// src/pages/Overview.js
import React, { useContext, useState, useEffect} from 'react';
import { Box, Drawer, List, ListItem, ListItemText, IconButton, CssBaseline, Toolbar, TextField, Radio, RadioGroup, FormControlLabel, FormControl, FormLabel, Checkbox, FormGroup } from '@mui/material';
import { ChevronLeft, ChevronRight } from '@mui/icons-material';
import AlertArea from "../components/AlertArea";
import EventFetcher from "../components/EventFetcher";
import { EventsContext } from '../contexts/EventsContext';
import '../styles/Overview.css';
import SearchBar from "../components/SearchBar";
import FilteredSearchBar from "../components/FilteredSearchBar";


const drawerWidth = 300; // Fixed width for the expanded drawer
const collapsedWidth = 60; // Fixed width for the collapsed drawer

const Overview = () => {
  const [sortCriterion, setSortCriterion] = useState('EXP');
  const { setSearchEventCriteria, searchEventCriteria, setSearchApplicationCriteria, searchApplicationCriteria,
    setSearchStatusCriteria, searchStatusCriteria, setSelectedTypes, selectedTypes,
    groupList, setSearchGroupCriteria, searchGroupCriteria,
    isDrawerOpen, setIsDrawerOpen, setShowLabels, showLabels} = useContext(EventsContext);
  const [transformedGroupList, setTransformedGroupList] = useState([]);


  useEffect(() => {
    if (groupList && Array.isArray(groupList)) {
      const transformedList = groupList.map(group => group.group_name);
      setTransformedGroupList(transformedList);
    }
  }, [groupList]);

  const toggleDrawer = () => {
    setIsDrawerOpen(!isDrawerOpen);
  };

  const handleSortChange = (event) => {
    setSortCriterion(event.target.value);
  };

  const handleTypeChange = (event) => {
    setSelectedTypes({
      ...selectedTypes,
      [event.target.name]: event.target.checked,
    });
  };

  const handleShowLabelsChange = (event) => {
    setShowLabels(event.target.checked);
  };

  const drawer = (
    <div>
      <div className="drawerHeader" style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'center', padding: '8px' }}>
        <IconButton onClick={toggleDrawer}>
          {isDrawerOpen ? <ChevronRight /> : <ChevronLeft />}
        </IconButton>
      </div>
      <Box p={2} display={isDrawerOpen ? 'block' : 'none'}>
        <Box mb={2}>
          <FilteredSearchBar label="Search Group" setSearchEntry={setSearchGroupCriteria}  options={transformedGroupList}/>
        </Box>
        <Box mb={2}>
          <SearchBar label="Search Application" setSearchEntry={setSearchApplicationCriteria} keyName={'appName'} initialValue={searchApplicationCriteria['appName']} />
        </Box>
        <Box mb={2}>
          <SearchBar label="Search Event" setSearchEntry={setSearchEventCriteria} keyName={'eventName'} initialValue={searchEventCriteria['eventName']} />
        </Box>
        <Box mb={2}>
          <SearchBar label="Search Status" setSearchEntry={setSearchStatusCriteria} keyName={'eventStatus'} initialValue={searchStatusCriteria['eventStatus']} />
        </Box>
        <Box mt={4}>
          <FormControl component="fieldset">
            <FormLabel component="legend">Sort Criteria</FormLabel>
            <RadioGroup aria-label="sort" name="sort" value={sortCriterion} onChange={handleSortChange}>
              <FormControlLabel value="EXP" control={<Radio />} label="EXP" />
              <FormControlLabel value="EVT" control={<Radio />} label="EVT" />
            </RadioGroup>
          </FormControl>
        </Box>
        <Box mt={4}>
          <FormControl component="fieldset">
            <FormLabel component="legend">Select Types</FormLabel>
            <FormGroup>
              <FormControlLabel
                control={<Checkbox checked={selectedTypes.EVT} onChange={handleTypeChange} name="EVT" />}
                label="EVT"
              />
              <FormControlLabel
                control={<Checkbox checked={selectedTypes.EXP} onChange={handleTypeChange} name="EXP" />}
                label="EXP"
              />
              <FormControlLabel
                control={<Checkbox checked={selectedTypes.SLO} onChange={handleTypeChange} name="SLO" />}
                label="SLO"
              />
              <FormControlLabel
                control={<Checkbox checked={selectedTypes.SLA} onChange={handleTypeChange} name="SLA" />}
                label="SLA"
              />
            </FormGroup>
          </FormControl>
        </Box>
        <Box mt={4}>
          <FormLabel component="legend">Labels</FormLabel>
          <FormControlLabel
            control={<Checkbox checked={showLabels} onChange={handleShowLabelsChange} name="showLabels" />}
            label="Show Labels"
          />
        </Box>
      </Box>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <CssBaseline />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          marginRight: isDrawerOpen ? `${collapsedWidth}px` : `${collapsedWidth}px`,
          transition: 'margin 0.3s',
        }}
      >
        <EventFetcher />
        <AlertArea />
      </Box>
      <Drawer
        sx={{
          width: isDrawerOpen ? drawerWidth : collapsedWidth,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: isDrawerOpen ? drawerWidth : collapsedWidth,
            boxSizing: 'border-box',
            marginTop: '68px', // Ensure it doesn't cover the TopBar
          },
        }}
        variant="permanent"
        anchor="right"
        open={isDrawerOpen}
      >
        {drawer}
      </Drawer>
    </Box>
  );
};

export default Overview;
