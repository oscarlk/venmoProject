import React from 'react';
import { AppBar, Toolbar, Typography, Box, IconButton, Avatar } from '@mui/material';
import SignOutOverlay from '../SignOut/SignOutOverlay';
import logo from '../../assets/logo.png';

const NavBar = () => {
  return (
    <AppBar position="static" color="#000" elevation={0} >
      <Toolbar sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>

        <Box component="img" src={logo} alt="Glance" sx={{width: {xs:'100px', md:'130px'}, mx:1}} />
        
        <Box>
          <SignOutOverlay />
        </Box>
      </Toolbar>
    </AppBar>
  );
};

export default NavBar;
