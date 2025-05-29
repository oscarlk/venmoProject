import React from 'react'
import { Container } from '@mui/material';
import styles from './Dashboard.module.css';
import NavBar from '../../components/NavBar/NavBar';
import venmo from '../../assets/venmo.png';
import Card from '../../components/Card/Card';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';


const Dashboard = () => {
  return (
    <>
        <NavBar />
        <Container maxWidth="xlg" className={styles.container}>
          
            <h1>Your <img src={venmo} alt="Venmo" width={130} /> history, at a glance.</h1>

        

            <Box sx={{ flexGrow: 1}}>
                <Grid container spacing={2} rowSpacing={4}>
                    {/* Top Row */}
                    <Grid size={3}>
                        <Card>Average Payment Completion</Card>
                    </Grid>
                    <Grid size={3}>
                        <Card>Total Transactions</Card>
                    </Grid>
                    <Grid size={3}>
                        <Card>Top people who paid you</Card>
                    </Grid>
                    <Grid size={3}>
                        <Card>Top people you paid</Card>
                    </Grid>
                
                    {/* Bottom Row */}
                    <Grid size={6}>
                        <Card>Transaction History</Card>
                    </Grid>
                    <Grid size={6}>
                        <Card>Your 6 month transaction history</Card>
                    </Grid>
                </Grid>
            </Box>
        </Container>
        
    </>
  )
}

export default Dashboard;
