import React, { useState, useEffect } from 'react'
import Container from '@mui/material/Container';
import styles from './Dashboard.module.css';
import NavBar from '../../components/NavBar/NavBar';
import venmo from '../../assets/venmo.png';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Grid';
import Chip from '@mui/material/Chip';
import { Typography, CircularProgress, Alert, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { BarChart } from '@mui/x-charts';
import { LineChart } from '@mui/x-charts/LineChart';
import TransactionTable from '../../components/TransactionTable/TransactionTable';
import Divider from '@mui/material/Divider';

import { useAuth } from '../../contexts/AuthContext';

const Div = styled('div')(({ theme }) => ({
    ...theme.typography.button,
    backgroundColor: (theme.vars || theme).palette.background.paper,
    padding: theme.spacing(1),
    textAlign: 'left',
}));


const Dashboard = () => {

    const { user } = useAuth();
    const [venmoData, setVenmoData] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const {
        allTransactions = [],
        averagePaybackTime = 0,
        paidCount= 0,
        paymentsReceived = 0,
        requestCount = 0,
        topPaidByMe = [],
        topPaidToMe = [],

    } = venmoData || {};

    useEffect(() => {
        if (user) {
            fetchVenmoData();
        }
    }, [user]); 

    const fetchVenmoData = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch('http://localhost:8000/getVenmoData', {
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json',
                }
            });

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || `HTTP ${response.status}`);
            }

            const data = await response.json();
            setVenmoData(data);
        } catch (err) {
            setError(err.message);
            console.error('Error fetching Venmo data:', err);
        } finally {
            setLoading(false);
        }
    };

    if (loading) {
        return (
            <>
                <NavBar />
                <Container maxWidth="lg" className={styles.container}>
                    <Box display="flex" flexDirection="column" alignItems="center" justifyContent="center" minHeight="50vh">
                        <CircularProgress size={60} />
                        <Typography variant="h6" sx={{ mt: 2 }}>
                            Loading your Venmo data...
                        </Typography>
                        <Typography variant="body2" color="textSecondary">
                            Analyzing your Gmail for Venmo transactions
                        </Typography>
                    </Box>
                </Container>
            </>
        );
    }

    // Show error state
    if (error) {
        return (
            <>
                <NavBar />
                <Container maxWidth="lg" className={styles.container}>
                    <Alert severity="error" sx={{ mt: 3 }}>
                        <Typography><strong>Error:</strong> {error}</Typography>
                        <Button onClick={fetchVenmoData} sx={{ mt: 1 }} variant="outlined" size="small">
                            Try Again
                        </Button>
                    </Alert>
                </Container>
            </>
        );
    }

    if (!venmoData) {
        return (
            <>
                <NavBar />
                <Container maxWidth="lg" className={styles.container}>
                    <Typography variant="h4" component="h1" sx={{ mt: 3, mb: 2, fontWeight: 'bolder' }}>
                        Your <img src={venmo} alt="Venmo" width={130} /> history, at a glance.
                    </Typography>
                    <Typography variant="body1" sx={{ mb: 2 }}>
                        Welcome, {user?.name}! Loading your transaction data...
                    </Typography>
                    <Button onClick={fetchVenmoData} variant="contained">
                        Load Venmo Data
                    </Button>
                </Container>
            </>
        );
    }

    const convertSeconds = (averagePaybackTime) => {
        const days = Math.floor(averagePaybackTime / 86400);
        const hours = Math.floor((averagePaybackTime % 86400) / 3600);
        const minutes = Math.floor((averagePaybackTime % 3600) / 60);
        const seconds = Math.round(averagePaybackTime % 60);
    
        return { days, hours, minutes, seconds };
      };

    const paybackTime = convertSeconds(averagePaybackTime);


      
    return (
        <>
            <NavBar />
            <Container maxWidth="lg" className={styles.container}>

                <Typography component="h1" sx={{ mt: 3, mb: 2, fontWeight: 'bolder', fontSize: {xs:'1.5rem', md:'2.5rem'}}}>Your <Box component="img" src={venmo} alt="Venmo" sx={{width: {xs:'100px', md:'130px'}, mx:1}} /> history, at a glance.</Typography>

                <Chip label="01/17/25 - 06/17/25" variant="outlined" color="info" />

                <Box sx={{ mt: 3, mb: 4,}} >
                    <Grid container spacing={2}>
                        {/* Top Row */}
                        <Grid item size={{xs:12, sm:6, lg:3}}>
                            <Card sx={{textAlign: 'center', height: '100%'}}>
                                <CardContent sx={{display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
                                    <Div>{"Average Payment Completion"}</Div>
                                    <Typography variant="h4" component="h4" sx={{ my: 5 }}>
                                        <Box component="span" >{paybackTime.days}</Box>
                                        <Box component="span" sx={{ color: '#A4A4A4', fontSize: '25px', mx: 0.5 }}>d </Box>
                                        <Box component="span" >{paybackTime.hours}</Box>
                                        <Box component="span" sx={{ color: '#A4A4A4', fontSize: '25px', mx: 0.5 }}>h </Box>
                                        <Box component="span" >{paybackTime.minutes}</Box>
                                        <Box component="span" sx={{ color: '#A4A4A4', fontSize: '25px', mx: 0.5 }}>m </Box>
                                        <Box component="span" >{paybackTime.seconds}</Box>
                                        <Box component="span" sx={{ color: '#A4A4A4', fontSize: '25px', mx: 0.5 }}>s</Box>
                                    </Typography>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item size={{xs:12, sm:6, lg:3}}>
                            <Card sx={{textAlign: 'center',display: 'flex', flexDirection: 'column', height: '100%'}}>
                                <CardContent>
                                    <Div>{"Total Transactions"}</Div>
                                    <Typography variant="h2" component="h1" color="textPrimary" sx={{ my: 1 }}>
                                        {paidCount + paymentsReceived || 'N/A'}
                                    </Typography>
                                    <Divider variant="middle" component="li" sx={{ listStyle: 'none' }} />
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1, p: 1 }}>
                                        <Typography variant="body1" component="span" color="textPrimary">
                                            {paidCount || 'N/A'}
                                        </Typography>
                                        <Typography variant="body1" component="span" color="textSecondary">
                                            Payments Made
                                        </Typography>
                                    </Box>
                                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 1, p: 1 }}>
                                        <Typography variant="body1" component="span" color="textPrimary">
                                            {paymentsReceived || 'N/A'}
                                        </Typography>
                                        <Typography variant="body1" component="span" color="textSecondary">
                                            Payments Received
                                        </Typography>
                                    </Box>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item size={{xs:12, sm:6, lg:3}}>
                            <Card sx={{height: '100%'}}>
                                <CardContent>
                                    <Div>{"Top people who paid you"}</Div>
                                    <BarChart
                                        xAxis={[{ data: [topPaidToMe[0]?.name, topPaidToMe[1]?.name, topPaidToMe[2]?.name] }]}
                                        series={[{ data: [topPaidToMe[0]?.total_amount, topPaidToMe[1]?.total_amount, topPaidToMe[2]?.total_amount], color:"#008CFF" }]}
                                        height={200}
                                        barLabel="value"
                                    />
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item size={{xs:12, sm:6, lg:3}}>
                            <Card sx={{height: '100%'}}>
                                <CardContent>
                                    <Div>{"Top people you paid"}</Div>
                                    <BarChart
                                        xAxis={[{ data: [topPaidByMe[0]?.name, topPaidByMe[1]?.name, topPaidByMe[2]?.name] }]}
                                        series={[{ data: [topPaidByMe[0]?.total_amount, topPaidByMe[1]?.total_amount, topPaidByMe[2]?.total_amount], color:"#008CFF" }]}
                                        height={200}
                                        barLabel="value"
                                    />
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                    <Grid container spacing={2} rowSpacing={4} sx={{ mt: 2 }}>
                        {/* Bottom Row */}
                        <Grid item size={{xs:12, lg:6}} >
                            <Card sx={{height: '100%'}}>
                                <CardContent>
                                    <Div>{"Transaction History"}</Div>
                                    <TransactionTable data={allTransactions}/>
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item size={{xs:12, lg:6}} >
                            <Card sx={{height: '100%'}}>
                                <CardContent>
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
                                                data: [6, 3, 7, 9.5, 4, 2],
                                                label: "Money Recieved",
                                                color: "green"
                                            },
                                            {
                                                curve: "linear",
                                                data: [5, -3, 9, 2, 9, -2],
                                                label: "Total Balance",
                                                color: "#008CFF"
                                            },
                                        ]}
                                        height={300}
                                        grid={{ vertical: true, horizontal: true }}
                                        legend={{ hidden: false }}
                                    />
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </Box>
            </Container>

        </>
    )
}

export default Dashboard;
