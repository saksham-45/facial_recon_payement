import React, { useState } from 'react';
import styled from 'styled-components';
import { Toaster } from 'react-hot-toast';
import FaceRecognition from './components/FaceRecognition';
import PaymentFlow from './components/PaymentFlow';
import { CreditCard, Camera, Home } from 'lucide-react';

const AppContainer = styled.div`
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
`;

const Header = styled.header`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
`;

const Logo = styled.h1`
  color: white;
  margin: 0;
  font-size: 1.8rem;
  font-weight: 700;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
`;

const Nav = styled.nav`
  display: flex;
  gap: 1rem;
`;

const NavButton = styled.button<{ active?: boolean }>`
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 25px;
  background: ${props => props.active 
    ? 'rgba(255, 255, 255, 0.2)' 
    : 'rgba(255, 255, 255, 0.1)'
  };
  color: white;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);

  &:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
  }
`;

const Main = styled.main`
  padding: 2rem;
`;

type Tab = 'home' | 'recognition' | 'payment';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<Tab>('home');

  const handleFaceDetected = (faces: any) => {
    console.log('Faces detected:', faces);
  };

  const handleFaceMatched = (matchResult: any) => {
    console.log('Face matched:', matchResult);
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'recognition':
        return (
          <FaceRecognition
            onFaceDetected={handleFaceDetected}
            onFaceMatched={handleFaceMatched}
          />
        );
      case 'payment':
        return <PaymentFlow />;
      default:
        return (
          <div style={{ textAlign: 'center', color: 'white', padding: '4rem 2rem' }}>
            <h1 style={{ fontSize: '3rem', marginBottom: '2rem' }}>
              🚀 FacePay
            </h1>
            <p style={{ fontSize: '1.2rem', marginBottom: '3rem', opacity: 0.9 }}>
              High-Performance Face Recognition Payment System
            </p>
            <div style={{ display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              <NavButton onClick={() => setActiveTab('recognition')}>
                <Camera size={24} />
                Face Recognition
              </NavButton>
              <NavButton onClick={() => setActiveTab('payment')}>
                <CreditCard size={24} />
                Payment Flow
              </NavButton>
            </div>
          </div>
        );
    }
  };

  return (
    <AppContainer>
      <Header>
        <Logo>FacePay</Logo>
        <Nav>
          <NavButton 
            active={activeTab === 'home'} 
            onClick={() => setActiveTab('home')}
          >
            <Home size={20} />
            Home
          </NavButton>
          <NavButton 
            active={activeTab === 'recognition'} 
            onClick={() => setActiveTab('recognition')}
          >
            <Camera size={20} />
            Recognition
          </NavButton>
          <NavButton 
            active={activeTab === 'payment'} 
            onClick={() => setActiveTab('payment')}
          >
            <CreditCard size={20} />
            Payment
          </NavButton>
        </Nav>
      </Header>

      <Main>
        {renderContent()}
      </Main>

      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
        }}
      />
    </AppContainer>
  );
};

export default App;
