import React, { useState, useEffect } from 'react';
import { Container, Box, Typography, Button, CircularProgress } from '@mui/material';
import { useSearchParams, useNavigate } from 'react-router-dom';
import LeaderboardCard from '../../components/Leaderboard/LeaderboardCard';
import { API_URL } from '../../config';
import logo from '../../assets/logo.png';

const PublicLeaderboard = () => {
    const [params] = useSearchParams();
    const rawRange = params.get('range');
    const range = ['1m', '6m', '1y'].includes(rawRange) ? rawRange : '6m';
    const [entries, setEntries] = useState([]);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        (async () => {
            setLoading(true);
            try {
                const res = await fetch(`${API_URL}/public/leaderboard?range=${range}`);
                if (res.ok) {
                    const d = await res.json();
                    setEntries(d.leaderboard || []);
                }
            } catch (err) {
                console.error('Public leaderboard fetch failed:', err);
            } finally {
                setLoading(false);
            }
        })();
    }, [range]);

    return (
        <Box sx={{ minHeight: '100vh', backgroundColor: '#F5FAFD', py: 6 }}>
            <Container maxWidth="sm" sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 3 }}>
                <Box component="img" src={logo} alt="Glance" sx={{ width: { xs: 160, md: 200 } }} />
                <Box sx={{ width: '100%' }}>
                    {loading ? (
                        <Box sx={{ display: 'flex', justifyContent: 'center', py: 6 }}>
                            <CircularProgress />
                        </Box>
                    ) : (
                        <LeaderboardCard entries={entries} range={range} />
                    )}
                </Box>
                <Button variant="contained" onClick={() => navigate('/signin')} sx={{ textTransform: 'none', fontWeight: 600 }}>
                    See your own Venmo stats →
                </Button>
            </Container>
        </Box>
    );
};

export default PublicLeaderboard;
