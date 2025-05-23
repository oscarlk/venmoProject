import { Avatar, Dialog, DialogContent, Button, IconButton, ButtonGroup, Container} from '@mui/material';
import { useState } from 'react';
import styles from './SignOutOverlay.module.css'; 

export default function SignOutOverlay() {
  const [open, setOpen] = useState(false);

  const buttons = [
    <Button  onClick={() => setOpen(false)} sx={{p: 2}} key="signOut">Sign Out</Button>,
   <Button  onClick={() => setOpen(false)} sx={{p: 2}} key="back">Back</Button>,
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
                <Avatar>JJ</Avatar>
            </IconButton>

            <Dialog 
                fullScreen
                open={open}
                onClose={() => setOpen(false)}
                PaperProps={{
                    sx: { backgroundColor: '#F5FAFD'},
                }}
            >
                <DialogContent sx={{ display: 'flex', flexDirection: 'column', alignItems: 'center', m: 'auto', justifyContent: 'center', height: '100vh', gap: '20px' }}>
                    <Avatar>JJ</Avatar>
                    <GroupOrientation />
                </DialogContent>
            </Dialog>
     
    </>
);
}
