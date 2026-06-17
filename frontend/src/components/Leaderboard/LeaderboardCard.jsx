import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Box from '@mui/material/Box';
import { Typography } from '@mui/material';
import { styled } from '@mui/material/styles';

const Div = styled('div')(({ theme }) => ({
    ...theme.typography.button,
    backgroundColor: (theme.vars || theme).palette.background.paper,
    padding: theme.spacing(1),
    textAlign: 'left',
}));

const rangeLabels = { '1m': '1 Month', '6m': '6 Month', '1y': '1 Year' };

const formatPayback = (secs) => {
    const days = Math.floor(secs / 86400);
    const hours = Math.floor((secs % 86400) / 3600);
    const minutes = Math.floor((secs % 3600) / 60);
    const seconds = Math.round(secs % 60);
    return `${days}d ${hours}h ${minutes}m ${seconds}s`;
};

// Shared ranked-list card used by both the dashboard and the public share page.
const LeaderboardCard = ({ entries = [], range = '6m', action = null }) => (
    <Card sx={{ height: '100%' }}>
        <CardContent>
            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Div>{"🏆 Biggest J'er"}</Div>
                {action}
            </Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1.5, px: 1 }}>
                Glance users ranked by average payback time ({rangeLabels[range]?.toLowerCase() || range}) — slowest first. 👀
            </Typography>
            {entries.length === 0 ? (
                <Typography variant="body2" color="text.secondary" sx={{ p: 1 }}>
                    No ranked users yet.
                </Typography>
            ) : (
                entries.map((u, i) => (
                    <Box
                        key={i}
                        sx={{
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between',
                            py: 1,
                            px: 1.5,
                            borderRadius: 1,
                            bgcolor: u.isYou ? 'rgba(0,140,255,0.08)' : 'transparent',
                            borderBottom: i < entries.length - 1 ? '1px solid rgba(0,0,0,0.06)' : 'none',
                        }}
                    >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                            <Typography sx={{ width: 28, textAlign: 'center', fontSize: '1.1rem' }}>
                                {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : i + 1}
                            </Typography>
                            <Typography sx={{ fontWeight: u.isYou ? 700 : 500 }}>
                                {u.name}{u.isYou ? ' (you)' : ''}
                            </Typography>
                        </Box>
                        <Typography sx={{ fontWeight: 600, color: '#008CFF' }}>
                            {formatPayback(u.averagePaybackTime)}
                        </Typography>
                    </Box>
                ))
            )}
        </CardContent>
    </Card>
);

export default LeaderboardCard;
