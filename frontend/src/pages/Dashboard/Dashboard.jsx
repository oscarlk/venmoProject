import React from 'react'
import Container from '@mui/material/Container';
import styles from './Dashboard.module.css';
import NavBar from '../../components/NavBar/NavBar';
import venmo from '../../assets/venmo.png';
import Card from '../../components/Card/Card';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Chip from '@mui/material/Chip';
import { Typography } from '@mui/material';
import { styled } from '@mui/material/styles';
import { BarChart } from '@mui/x-charts';
import { LineChart } from '@mui/x-charts/LineChart';

const Div = styled('div')(({ theme }) => ({
    ...theme.typography.button,
    backgroundColor: (theme.vars || theme).palette.background.paper,
    padding: theme.spacing(1),
  }));


const Dashboard = () => {
  return (
    <>
        <NavBar />
        <Container maxWidth="lg" className={styles.container}>
          
            <Typography variant="h4" component="h1" sx={{mt: 3, mb: 3, fontWeight: 'bolder'}}>Your <img src={venmo} alt="Venmo" width={130} /> history, at a glance.</Typography>

            <Chip  label="01/17/25 - 06/17/25" variant="outlined" color="info" />
        
            <Box sx={{ flexGrow: 1, mt: 4}}>
                <Grid container spacing={2} rowSpacing={4}>
                    {/* Top Row */}
                    <Grid size={3}>
                        <Card>
                            <Div>{"Average Payment Completion"}</Div>
                        </Card>
                    </Grid>
                    <Grid size={3}>
                        <Card>
                            <Div>{"Total Transactions"}</Div>

                        </Card>
                    </Grid>
                    <Grid size={3}>
                        <Card>
                            <Div>{"Top people who paid you"}</Div>
                            <BarChart
                                xAxis={[{ data: ['Oscar', 'Lee', 'Khowong'] }]}
                                series={[{ data: [4, 5, 6] }]}
                                height={200}
                                barLabel="value"
                            />

                        </Card>
                    </Grid>
                    <Grid size={3}>
                        <Card>
                            <Div>{"Top people you paid"}</Div>
                            <BarChart
                                xAxis={[{ data: ['Oscar', 'Lee', 'Khowong'] }]}
                                series={[{ data: [4, 5, 6] }]}
                                height={200}
                                barLabel="value"
                            />

                        </Card>
                    </Grid>
                
                    {/* Bottom Row */}
                    <Grid size={6}>
                        <Card>Transaction History</Card>
                    </Grid>
                    <Grid size={6}>
                        <Card>Your 6 month transaction history
                            <LineChart
                                xAxis={[{ 
                                    scaleType: "point",
                                    data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] 
                                }]}
                                series={[
                                    {
                                        curve: "linear", 
                                        data: [2, 5.5, 2, 8.5, 1.5, 5],
                                    },
                                    { 
                                        curve: "linear", 
                                        data: [6, 3, 7, 9.5, 4, 2] 
                                    },
                                    { 
                                        curve: "linear", 
                                        data: [5, -3, 9, 2, 9, -2]
                                    },
                                ]}
                                height={300}
                                grid={{ vertical: true, horizontal: true }}
                            />
                        </Card>
                    </Grid>
                </Grid>
            </Box>
        </Container>
        
    </>
  )
}

export default Dashboard;
