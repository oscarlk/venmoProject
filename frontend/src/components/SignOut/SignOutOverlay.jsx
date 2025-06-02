import { Avatar, Dialog, DialogContent, Button, IconButton, ButtonGroup, Container } from '@mui/material';
import { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

import styles from './SignOutOverlay.module.css';

export default function SignOutOverlay() {
    const { user, signOut } = useAuth();
    const [open, setOpen] = useState(false);

    const buttons = [
        <Button onClick={signOut} sx={{ p: 2 }} key="signOut">Sign Out</Button>,
        <Button onClick={() => setOpen(false)} sx={{ p: 2 }} key="back">Back</Button>,
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


    return (
        <>
            <IconButton onClick={() => setOpen(true)}>
                <Avatar src={user?.picture}></Avatar>
            </IconButton>

            <Dialog
                fullScreen
                open={open}
                onClose={() => setOpen(false)}
                PaperProps={{
                    sx: { backgroundColor: '#F5FAFD' },
                }}
            >
                <DialogContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', m: 'auto', justifyContent: 'center', height: '100vh', gap: '20px' }}>
                    <Avatar src={user?.picture}></Avatar>
                    <GroupOrientation />
                </DialogContent>
            </Dialog>
        </>
    );
}
