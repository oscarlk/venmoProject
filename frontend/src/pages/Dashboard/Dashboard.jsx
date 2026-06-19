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
import { Typography, CircularProgress, Alert, Button, ToggleButton, ToggleButtonGroup } from '@mui/material';
import { styled } from '@mui/material/styles';
import { BarChart } from '@mui/x-charts';
import { LineChart } from '@mui/x-charts/LineChart';
import TransactionTable from '../../components/TransactionTable/TransactionTable';
import Divider from '@mui/material/Divider';

import { useAuth } from '../../contexts/AuthContext';
import { API_URL } from '../../config';
import LeaderboardCard from '../../components/Leaderboard/LeaderboardCard';

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
    const [range, setRange] = useState('6m');
    const [leaderboard, setLeaderboard] = useState([]);
    const [shareCopied, setShareCopied] = useState(false);
    const [chartMetrics, setChartMetrics] = useState(['net']); // which lines to show

    const rangeLabels = { '1m': '1 Month', '6m': '6 Month', '1y': '1 Year' };

    const {
        allTransactions = [],
        averagePaybackTime = 0,
        paidCount= 0,
        paymentsReceived = 0,
        requestCount = 0,
        topPaidByMe = [],
        topPaidToMe = [],
        monthlyTotals = []

    } = venmoData || {};

    const months = monthlyTotals.map(item => {
        const [year, month] = item.month.split('-');
        const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                        'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return monthNames[parseInt(month) - 1];
    });

    const moneySpent = monthlyTotals.map(item => -1 * item.moneySpent);
    const moneyReceived = monthlyTotals.map(item => item.moneyReceived);
    const totalBalance = monthlyTotals.map(item => item.totalBalance);

    // Toggleable lines for the spending chart (starts with just Net Total).
    const chartMetricOrder = ['net', 'in', 'out'];
    const chartMetricDefs = {
        net: { label: 'Net Total', color: '#008CFF', data: totalBalance },
        in:  { label: 'Money In',  color: 'green',   data: moneyReceived },
        out: { label: 'Money Out', color: 'red',     data: moneySpent },
    };
    const toggleChartMetric = (id) => {
        setChartMetrics((prev) =>
            prev.includes(id)
                ? (prev.length > 1 ? prev.filter((m) => m !== id) : prev) // keep ≥1 line
                : [...prev, id]
        );
    };

    useEffect(() => {
        if (user) {
            fetchVenmoData();
        }
    }, [user, range]);

    const fetchLeaderboard = async () => {
        try {
            const res = await fetch(`${API_URL}/leaderboard?range=${range}`, {
                credentials: 'include',
                headers: { 'Content-Type': 'application/json' },
            });
            if (res.ok) {
                const d = await res.json();
                setLeaderboard(d.leaderboard || []);
            }
        } catch (err) {
            console.error('Leaderboard fetch failed:', err);
        }
    };

    const fetchVenmoData = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await fetch(`${API_URL}/getVenmoData?range=${range}`, {
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
            // refresh leaderboard after our own entry is updated server-side
            fetchLeaderboard();
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

    const handleShare = async () => {
        const url = `${window.location.origin}/l?range=${range}`;
        const shareData = {
            title: "Glance — Biggest J'er leaderboard",
            url,
        };
        try {
            if (navigator.share) {
                await navigator.share(shareData);
            } else {
                await navigator.clipboard.writeText(url);
                setShareCopied(true);
                setTimeout(() => setShareCopied(false), 2000);
            }
        } catch (err) {
            // user dismissed the share sheet — ignore
        }
    };

    const shareButton = (
        <Button onClick={handleShare} size="small" sx={{ textTransform: 'none' }}
            startIcon={
                <Box component="svg" viewBox="0 0 24 24" sx={{ width: 18, height: 18, fill: 'currentColor' }}>
                    <path d="M18 16.08c-.76 0-1.44.3-1.96.77L8.91 12.7c.05-.23.09-.46.09-.7s-.04-.47-.09-.7l7.05-4.11c.54.5 1.25.81 2.04.81 1.66 0 3-1.34 3-3s-1.34-3-3-3-3 1.34-3 3c0 .24.04.47.09.7L8.04 9.81C7.5 9.31 6.79 9 6 9c-1.66 0-3 1.34-3 3s1.34 3 3 3c.79 0 1.5-.31 2.04-.81l7.12 4.16c-.05.21-.08.43-.08.65 0 1.61 1.31 2.92 2.92 2.92s2.92-1.31 2.92-2.92-1.31-2.92-2.92-2.92z" />
                </Box>
            }
        >
            {shareCopied ? 'Link copied!' : 'Share'}
        </Button>
    );

    const hasData = allTransactions.length > 0;
    const formatDate = (d) => `${d.getMonth() + 1}/${d.getDate()}/${d.getFullYear().toString().slice(-2)}`;
    const formattedEarliestDate = hasData ? formatDate(new Date(allTransactions[allTransactions.length - 1].dateRequested)) : '';
    const formattedMostRecentDate = hasData ? formatDate(new Date(allTransactions[0].dateRequested)) : '';

    const handleRangeChange = (event, newRange) => {
        if (newRange !== null) setRange(newRange);
    };

    const rangePills = (
        <ToggleButtonGroup
            value={range}
            exclusive
            onChange={handleRangeChange}
            size="small"
            color="primary"
        >
            <ToggleButton value="1m" sx={{ textTransform: 'none', px: 2 }}>1M</ToggleButton>
            <ToggleButton value="6m" sx={{ textTransform: 'none', px: 2 }}>6M</ToggleButton>
            <ToggleButton value="1y" sx={{ textTransform: 'none', px: 2 }}>1Y</ToggleButton>
        </ToggleButtonGroup>
    );

    return (
        <>
            <NavBar />
            <Container maxWidth="lg" className={styles.container}>

                <Typography component="h1" sx={{ mt: 3, mb: 2, fontWeight: 'bolder', fontSize: {xs:'1.5rem', md:'2.5rem'}}}>Your <Box component="img" src={venmo} alt="Venmo" sx={{width: {xs:'100px', md:'130px'}, mx:1}} /> history, at a glance.</Typography>

                <Box sx={{ display: 'flex', flexWrap: 'wrap', alignItems: 'center', gap: 2 }}>
                    {rangePills}
                    {hasData && <Chip label={`${formattedEarliestDate} - ${formattedMostRecentDate}`} variant="outlined" color="info" />}
                </Box>

                {!hasData && (
                    <Alert severity="info" sx={{ mt: 3 }}>
                        No Venmo transactions found in the last {rangeLabels[range].toLowerCase()}. Try a longer range.
                    </Alert>
                )}

                {hasData && <Box sx={{ mt: 3, mb: 4,}} >
                    <Grid container spacing={2} sx={{ mb: 2 }}>
                        {/* Leaderboard Row */}
                        <Grid item size={{xs:12}}>
                            <LeaderboardCard entries={leaderboard} range={range} action={shareButton} />
                        </Grid>
                    </Grid>
                    <Grid container spacing={2}>
                        {/* Top Row */}
                        <Grid item size={{xs:12, sm:6, lg:3}}>
                            <Card sx={{textAlign: 'center', height: '100%'}}>
                                <CardContent sx={{display: 'flex', flexDirection: 'column', justifyContent: 'center'}}>
                                    <Div>{"Average Payback Time"}</Div>
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
                                    <Div>{"Who Pays You Most"}</Div>
                                    <BarChart
                                        xAxis={[{ data: [topPaidToMe[0]?.name, topPaidToMe[1]?.name, topPaidToMe[2]?.name], valueFormatter: (value) => value ? value.split(' ')[0].charAt(0).toUpperCase() + value.split(' ')[0].slice(1) : '' }]}
                                        series={[{ data: [topPaidToMe[0]?.total_amount, topPaidToMe[1]?.total_amount, topPaidToMe[2]?.total_amount], color:"#008CFF", valueFormatter: (value) => '$' + value }]}
                                        height={200}
                                        barLabel="value"
                                    />
                                </CardContent>
                            </Card>
                        </Grid>
                        <Grid item size={{xs:12, sm:6, lg:3}}>
                            <Card sx={{height: '100%'}}>
                                <CardContent>
                                    <Div>{"Who You Pay Most"}</Div>
                                    <BarChart
                                        xAxis={[{ data: [topPaidByMe[0]?.name, topPaidByMe[1]?.name, topPaidByMe[2]?.name], valueFormatter: (value) => value ? value.split(' ')[0].charAt(0).toUpperCase() + value.split(' ')[0].slice(1) : '' }]}
                                        series={[{ data: [topPaidByMe[0]?.total_amount, topPaidByMe[1]?.total_amount, topPaidByMe[2]?.total_amount], color:"#008CFF", valueFormatter: (value) => '$' + value }]}
                                        height={200}
                                        barLabel={"value"}
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
                                    <Div>{`Your ${rangeLabels[range]} Spending Totals`}</Div>
                                    <Box sx={{ display: 'flex', gap: 1, mt: 1, mb: 0.5, flexWrap: 'wrap' }}>
                                        {chartMetricOrder.map((id) => {
                                            const m = chartMetricDefs[id];
                                            const active = chartMetrics.includes(id);
                                            return (
                                                <Chip
                                                    key={id}
                                                    label={m.label}
                                                    size="small"
                                                    onClick={() => toggleChartMetric(id)}
                                                    variant={active ? 'filled' : 'outlined'}
                                                    sx={{
                                                        fontWeight: 600,
                                                        borderColor: m.color,
                                                        color: active ? '#fff' : m.color,
                                                        backgroundColor: active ? m.color : 'transparent',
                                                        '&:hover': { backgroundColor: active ? m.color : 'rgba(0,0,0,0.04)' },
                                                    }}
                                                />
                                            );
                                        })}
                                    </Box>
                                    <LineChart
                                        xAxis={[{
                                            scaleType: "point",
                                            data: months,
                                        }]}
                                        series={chartMetricOrder
                                            .filter((id) => chartMetrics.includes(id))
                                            .map((id) => ({
                                                curve: "linear",
                                                data: chartMetricDefs[id].data,
                                                label: chartMetricDefs[id].label,
                                                color: chartMetricDefs[id].color,
                                            }))}
                                        height={300}
                                        grid={{ vertical: true, horizontal: true }}
                                        legend={{ hidden: true }}
                                    />
                                </CardContent>
                            </Card>
                        </Grid>
                    </Grid>
                </Box>}
            </Container>

        </>
    )
}

export default Dashboard;
