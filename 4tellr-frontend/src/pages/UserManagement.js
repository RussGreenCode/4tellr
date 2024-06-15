// src/pages/UserManagement.js
import React, {useState, useContext, useEffect} from 'react';
import { Box, Button, Typography, TextField, List, ListItem, ListItemText } from '@mui/material';
import axios from 'axios';
import '../styles/UserManagement.css';

const UserManagement = () => {
  const [emailList, setEmailList] = useState('');
  const [users, setUsers] = useState([]);
  const [statusMessages, setStatusMessages] = useState([]);

  useEffect(() => {
      getUsers()
  }, []);

  const getUsers = async () => {
     try {
      const response = await axios.get('http://127.0.0.1:5000/api/get_users');
      const allUsers = response.data;
      setUsers(allUsers);
    } catch (error) {
      console.error('Error adding users:', error);
    }
  }

  const handleAddUsers = async () => {
    const emails = emailList.split(',').map(email => email.trim());
    try {
      const response = await axios.post('http://127.0.0.1:5000/api/add_users', { emails });
      setStatusMessages(response.data.map(status => ({
        email: status.email,
        status: status.success ? 'success' : 'error',
        message: status.message
      })));
      getUsers();
      setEmailList('');
    } catch (error) {
      console.error('Error adding users:', error);
    }
  };

  const handleDeleteUser = async (userToDelete) => {
    try {
      const response = await axios.delete(`http://127.0.0.1:5000/api/delete_user/${userToDelete.email}`);
      setStatusMessages(response.data.map(status => ({
        email: status.email,
        status: status.success ? 'success' : 'error',
        message: status.message
      })));
      getUsers();
    } catch (error) {
      console.error('Error deleting user:', error);
      setStatusMessages([...statusMessages, {
        email: userToDelete.email,
        status: 'error',
        message: `Failed to delete user ${userToDelete.email}: ${error.message}`
      }]);
      getUsers();
    }
  };

  return (
    <Box p={2}>
      <Typography variant="h4" gutterBottom>
        Manage Users
      </Typography>
      <Box mb={2}>
        <TextField
          label="Emails (comma separated)"
          value={emailList}
          onChange={(e) => setEmailList(e.target.value)}
          variant="outlined"
          fullWidth
        />
      </Box>
      <Box mt={2}>
        <Button
          variant="contained"
          color="primary"
          onClick={handleAddUsers}
          disabled={!emailList}
        >
          Add Users
        </Button>
      </Box>
      <Box mt={4}>
        <Typography variant="h5" gutterBottom>
          Status Messages
        </Typography>
        <List>
          {statusMessages.map((status, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={`${status.email} - ${status.message}`}
                primaryTypographyProps={{ color: status.status === 'success' ? 'green' : 'red' }}
              />
            </ListItem>
          ))}
        </List>
      </Box>
      <Box mt={4}>
        <Typography variant="h5" gutterBottom>
          Existing Users
        </Typography>
        <List>
          {users.map((user, index) => (
            <ListItem key={index} button>
              <ListItemText primary={user.email} />
              <Button variant="contained" color="secondary" onClick={() => handleDeleteUser(user)}>
                Delete
              </Button>
            </ListItem>
          ))}
        </List>
      </Box>
    </Box>
  );
};

export default UserManagement;
