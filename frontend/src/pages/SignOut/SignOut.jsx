import React from 'react';
import { Container } from '@mui/material';
import styles from './SignOut.module.css'; 
import Avatar from '@mui/material/Avatar';
import Button from '@mui/material/Button';
import ButtonGroup from '@mui/material/ButtonGroup';


const buttons = [
 <Button sx={{p: 2}} key="signOut">Sign Out</Button>,
<Button sx={{p: 2}} key="back">Back</Button>,
];
  
function GroupOrientation() {
    return (
        <ButtonGroup
          orientation="vertical"
          aria-label="Vertical button group"
          variant="text"
        >
          {buttons}
        </ButtonGroup>
    );
  }


const SignOut = () => {
    return (
        <Container maxWidth="xlg" className={styles.container}>
            <Avatar>JJ</Avatar>
            <GroupOrientation />
        </Container>
    );
};

export default SignOut;

