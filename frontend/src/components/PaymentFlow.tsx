import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { CreditCard, User, CheckCircle, XCircle, Loader, DollarSign } from 'lucide-react';
import toast from 'react-hot-toast';

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  color: white;
`;

const PaymentCard = styled.div`
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-radius: 20px;
  padding: 2rem;
  margin: 1rem 0;
  min-width: 400px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
`;

const Input = styled.input`
  width: 100%;
  padding: 1rem;
  margin: 0.5rem 0;
  border: none;
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  font-size: 1rem;
  backdrop-filter: blur(10px);

  &::placeholder {
    color: rgba(255, 255, 255, 0.7);
  }

  &:focus {
    outline: none;
    background: rgba(255, 255, 255, 0.2);
  }
`;

const Button = styled.button<{ variant?: 'primary' | 'success' | 'danger' }>`
  width: 100%;
  padding: 1rem;
  margin: 0.5rem 0;
  border: none;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: ${props => {
    switch (props.variant) {
      case 'success': return 'linear-gradient(45deg, #4CAF50, #45a049)';
      case 'danger': return 'linear-gradient(45deg, #f44336, #da190b)';
      default: return 'linear-gradient(45deg, #ff6b6b, #ee5a24)';
    }
  }};
  color: white;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.3);
  }

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
    transform: none;
  }
`;

const StatusIndicator = styled.div<{ status: 'idle' | 'processing' | 'success' | 'error' }>`
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  border-radius: 10px;
  margin: 1rem 0;
  background: ${props => {
    switch (props.status) {
      case 'processing': return 'rgba(255, 193, 7, 0.2)';
      case 'success': return 'rgba(76, 175, 80, 0.2)';
      case 'error': return 'rgba(244, 67, 54, 0.2)';
      default: return 'rgba(255, 255, 255, 0.1)';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'processing': return '#ffc107';
      case 'success': return '#4CAF50';
      case 'error': return '#f44336';
      default: return 'white';
    }
  }};
`;

const PaymentFlow: React.FC = () => {
  const [amount, setAmount] = useState('');
  const [merchantId, setMerchantId] = useState('');
  const [paymentStatus, setPaymentStatus] = useState<'idle' | 'processing' | 'success' | 'error'>('idle');
  const [faceDetected, setFaceDetected] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);

  // Simulate face detection for payment
  useEffect(() => {
    const interval = setInterval(() => {
      // Simulate random face detection
      if (Math.random() > 0.7) {
        setFaceDetected(true);
        setUserId('user_' + Math.floor(Math.random() * 1000));
      } else {
        setFaceDetected(false);
        setUserId(null);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, []);

  const handlePayment = async () => {
    if (!amount || !merchantId) {
      toast.error('Please fill in all fields');
      return;
    }

    if (!faceDetected) {
      toast.error('No face detected. Please look at the camera.');
      return;
    }

    setPaymentStatus('processing');

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 2000));

      const response = await fetch('http://localhost:8000/transactions/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          user_id: parseInt(userId?.replace('user_', '') || '1'),
          merchant_id: parseInt(merchantId),
          amount: parseFloat(amount),
        }),
      });

      if (response.ok) {
        setPaymentStatus('success');
        toast.success('Payment successful!');
      } else {
        throw new Error('Payment failed');
      }
    } catch (error) {
      setPaymentStatus('error');
      toast.error('Payment failed. Please try again.');
    }
  };

  const resetPayment = () => {
    setPaymentStatus('idle');
    setAmount('');
    setMerchantId('');
  };

  return (
    <Container>
      <h1>💳 FacePay Payment</h1>

      <PaymentCard>
        <h2>Payment Details</h2>
        
        <Input
          type="number"
          placeholder="Amount (₹)"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
        />
        
        <Input
          type="number"
          placeholder="Merchant ID"
          value={merchantId}
          onChange={(e) => setMerchantId(e.target.value)}
        />

        <StatusIndicator status={faceDetected ? 'success' : 'error'}>
          {faceDetected ? <CheckCircle size={20} /> : <XCircle size={20} />}
          {faceDetected ? `Face Detected (User: ${userId})` : 'No Face Detected'}
        </StatusIndicator>

        <Button
          onClick={handlePayment}
          disabled={!faceDetected || paymentStatus === 'processing'}
          variant={paymentStatus === 'success' ? 'success' : 'primary'}
        >
          {paymentStatus === 'processing' ? (
            <Loader size={20} className="animate-spin" />
          ) : (
            <CreditCard size={20} />
          )}
          {paymentStatus === 'processing' 
            ? 'Processing...' 
            : paymentStatus === 'success' 
            ? 'Payment Successful!' 
            : 'Pay with Face'
          }
        </Button>

        {paymentStatus === 'success' && (
          <Button onClick={resetPayment} variant="secondary">
            New Payment
          </Button>
        )}
      </PaymentCard>

      <PaymentCard>
        <h3>Quick Test Data</h3>
        <p>Use these IDs for testing:</p>
        <ul style={{ textAlign: 'left', opacity: 0.8 }}>
          <li>Merchant ID: 1 (Canteen)</li>
          <li>User ID: Auto-detected from face</li>
          <li>Amount: Any positive number</li>
        </ul>
      </PaymentCard>
    </Container>
  );
};

export default PaymentFlow;
