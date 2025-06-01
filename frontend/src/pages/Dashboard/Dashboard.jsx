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
import TransactionTable from '../../components/TransactionTable/TransactionTable';
import Divider from '@mui/material/Divider';


const Div = styled('div')(({ theme }) => ({
    ...theme.typography.button,
    backgroundColor: (theme.vars || theme).palette.background.paper,
    padding: theme.spacing(1),
    textAlign: 'left',
  }));


const Dashboard = () => {
  return (
    <>
        <NavBar />
        <Container maxWidth="lg" className={styles.container}>
          
            <Typography variant="h4" component="h1" sx={{mt: 3, mb: 2, fontWeight: 'bolder'}}>Your <img src={venmo} alt="Venmo" width={130} /> history, at a glance.</Typography>

            <Chip  label="01/17/25 - 06/17/25" variant="outlined" color="info" />
        
            <Box rowSpacing= {1} sx={{ mt: 3, mb: 4 }} > 
                <Grid container spacing={2} rowSpacing={4} alignItems={"stretch"}> 
                    {/* Top Row */}
                    <Grid item size={3}>
                        <Card >
                            <Div>{"Average Payment Completion"}</Div>
                            <Typography variant="h1" component="h1" color="textPrimary" sx={{ mt: 1 }}>
                                5
                            </Typography>
                            <Typography variant="h6" component="h6" sx={{ mt: 1 }}>
                                Days
                            </Typography>
                        </Card>
                    </Grid>
                    <Grid item size={3}>
                        <Card>
                            <Div>{"Total Transactions"}</Div>
                            <Typography variant="h1" component="h1" color="textPrimary" sx={{ mt: 1 }}>
                                32
                            </Typography>
                            <Divider variant="middle" component="li" sx={{ listStyle: 'none' }}/>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1 , p: 1 }}>
                                <Typography variant="body1" component="span" color="textPrimary">
                                    20
                                </Typography>
                                <Typography variant="body1" component="span" color="textSecondary">
                                    Payments Made
                                </Typography>
                            </Box>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1, p: 1}}>
                                <Typography variant="body1" component="span" color="textPrimary">
                                    12
                                </Typography>
                                <Typography variant="body1" component="span" color="textSecondary">
                                    Payments Recieved
                                </Typography>
                            </Box>
                        </Card>
                    </Grid>
                    <Grid item size={3}>
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
                    <Grid item size={3}>
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
                </Grid>
                <Grid container spacing={2} rowSpacing={4} sx={{mt: 1}}> 
                
                    {/* Bottom Row */}
                    <Grid item size={6}>
                        <Card>
                        <Div>{"Transaction History"}</Div>
                        <TransactionTable />
                            
                        </Card>
                    </Grid>
                    <Grid item size={6}>
                        <Card>
                            <Div>{"Your 6 Month Spending Totals"}</Div>
                            <LineChart
                                xAxis={[{ 
                                    scaleType: "point",
                                    data: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'] 
                                }]}
                                series={[
                                    {
                                        curve: "linear", 
                                        data: [2, 5.5, 2, 8.5, 1.5, 5],
                                        label: "Money Spent",
                                        color: "red"
                                    },
                                    { 
                                        curve: "linear", 
                                        data: [6, 3, 7, 9.5, 4, 2] ,
                                        label: "Money Recieved",
                                        color: "green"
                                    },
                                    { 
                                        curve: "linear", 
                                        data: [5, -3, 9, 2, 9, -2],
                                        label: "Total Balance",
                                        color: "blue"
                                    },
                                ]}
                                height={300}
                                grid={{ vertical: true, horizontal: true }}
                                legend={{ hidden: false }}
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
