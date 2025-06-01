import React from 'react';
import { AppBar, Toolbar, Typography, Box, IconButton, Avatar } from '@mui/material';
import SignOutOverlay from '../SignOut/SignOutOverlay';

const NavBar = () => {
  return (
    <AppBar position="static" color="#000" elevation={1} >
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between' }}>
        
        <Typography variant="h6" component="div" sx={{ fontWeight: 'bold' }}>
          Stealth Project
        </Typography>

        <Box>
          <SignOutOverlay />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default NavBar;
