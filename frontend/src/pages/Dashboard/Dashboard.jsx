import React from 'react'
import { Container } from '@mui/material';
import styles from './Dashboard.module.css';
import NavBar from '../../components/NavBar/NavBar';
import venmo from '../../assets/venmo.png';



const Dashboard = () => {
  return (
    <>
        <NavBar />
        <Container maxWidth="lg" className={styles.container}>
          
            <h1>Your <img src={venmo} alt="Venmo" width={130} /> history, at a glance.</h1>

        </Container>
    </>
  )
}

export default Dashboard;
