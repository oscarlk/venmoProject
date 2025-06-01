import React from 'react';
import { Paper } from '@mui/material';
import { styled } from '@mui/material/styles';


const Card = styled(Paper)(({ theme }) => ({
  backgroundColor: '#fff',
  padding: theme.spacing(2),
  textAlign: 'center',
  color: theme.palette.text.secondary,
  display: 'flex',
  flexDirection: 'column',
  height: '87%',
}));

export default Card;