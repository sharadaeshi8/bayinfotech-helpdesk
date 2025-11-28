import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Box,
  Paper,
  Typography,
  Chip,
  Grid,
  Button,
  Divider,
  Container,
  CircularProgress
} from '@mui/material';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber';
import PersonIcon from '@mui/icons-material/Person';
import AccessTimeIcon from '@mui/icons-material/AccessTime';
import TagIcon from '@mui/icons-material/Label';
import { getTickets } from '../api/ticket';

const TicketDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchTicketDetails = async () => {
      setLoading(true);
      try {
        // Try to fetch from backend first
        const allTickets = await getTickets();
        const foundTicket = allTickets.find(t => t.id === id);
        
        if (foundTicket) {
          setTicket({
            ...foundTicket,
            // Ensure tags are in correct format
            tags: foundTicket.tags || [],
            // Format date
            createdAt: new Date(foundTicket.created_at).toLocaleString(),
            reporter: 'Current User', // Backend doesn't store this yet
            assignee: 'Unassigned'
          });
        } else {
          // Fallback to mock if not found (or show error)
          // For demo purposes, we'll generate a mock one if not found
          const mockTicket = {
            id: id,
            title: 'Issue reported via AI Chat',
            description: 'This ticket was automatically generated following a conversation with the AI Assistant. The user reported an issue that required escalation or formal tracking.',
            status: 'Open',
            priority: 'High',
            tier: 'Tier 1',
            createdAt: new Date().toLocaleString(),
            reporter: 'Current User',
            assignee: 'Unassigned',
            tags: [
              { label: 'AI Generated', confidence: 100 },
              { label: 'Escalation', confidence: 95 }
            ],
            sentiment: 'Neutral'
          };
          setTicket(mockTicket);
        }
      } catch (error) {
        console.error("Error fetching ticket details:", error);
        // Fallback to mock on error
         const mockTicket = {
            id: id,
            title: 'Error loading ticket',
            description: 'Could not load ticket details from server.',
            status: 'Unknown',
            priority: 'Low',
            tier: 'Tier 0',
            createdAt: new Date().toLocaleString(),
            reporter: 'System',
            assignee: 'System',
            tags: [],
            sentiment: 'Neutral'
          };
          setTicket(mockTicket);
      } finally {
        setLoading(false);
      }
    };

    fetchTicketDetails();
  }, [id]);

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'Critical': return '#D32F2F';
      case 'High': return '#FF9500';
      case 'Medium': return '#FBC02D';
      case 'Low': return '#4A7C59';
      default: return '#999999';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Open': return '#FF9500';
      case 'In Progress': return '#2196F3';
      case 'Resolved': return '#4A7C59';
      default: return '#999999';
    }
  };

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', bgcolor: '#1a1a1a' }}>
        <CircularProgress sx={{ color: '#D4AF37' }} />
      </Box>
    );
  }

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#1a1a1a', p: 4 }}>
      <Container maxWidth="lg">
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={() => navigate('/tickets')}
          sx={{ color: '#999999', mb: 3, '&:hover': { color: '#D4AF37' } }}
        >
          Back to Dashboard
        </Button>

        <Paper sx={{ p: 4, bgcolor: '#242424', border: '1px solid #333333', borderRadius: 2 }}>
          {/* Header */}
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 4 }}>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <ConfirmationNumberIcon sx={{ fontSize: 40, color: '#D4AF37' }} />
              <Box>
                <Typography variant="h4" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 1 }}>
                  {ticket.id}
                </Typography>
                <Typography variant="h5" sx={{ color: '#E0E0E0' }}>
                  {ticket.title}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 2 }}>
              <Chip 
                label={ticket.priority} 
                sx={{ bgcolor: getPriorityColor(ticket.priority), color: '#fff', fontWeight: 'bold' }} 
              />
              <Chip 
                label={ticket.status} 
                sx={{ bgcolor: getStatusColor(ticket.status), color: '#fff', fontWeight: 'bold' }} 
              />
            </Box>
          </Box>

          <Divider sx={{ bgcolor: '#333333', mb: 4 }} />

          <Grid container spacing={4}>
            {/* Main Content */}
            <Grid item xs={12} md={8}>
              <Box sx={{ mb: 4 }}>
                <Typography variant="h6" sx={{ color: '#D4AF37', mb: 2 }}>Description</Typography>
                <Typography variant="body1" sx={{ color: '#E0E0E0', lineHeight: 1.6 }}>
                  {ticket.description}
                </Typography>
              </Box>

              <Box>
                <Typography variant="h6" sx={{ color: '#D4AF37', mb: 2 }}>AI Analysis</Typography>
                <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                  {ticket.tags.map((tag, idx) => (
                    <Chip
                      key={idx}
                      icon={<TagIcon />}
                      label={`${tag.label} (${tag.confidence}%)`}
                      sx={{ bgcolor: '#333333', color: '#D4AF37' }}
                    />
                  ))}
                </Box>
              </Box>
            </Grid>

            {/* Sidebar */}
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, bgcolor: '#1a1a1a', border: '1px solid #333333' }}>
                <Typography variant="h6" sx={{ color: '#D4AF37', mb: 3 }}>Details</Typography>
                
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PersonIcon sx={{ color: '#999999', mr: 2 }} />
                  <Box>
                    <Typography variant="caption" sx={{ color: '#999999', display: 'block' }}>Reporter</Typography>
                    <Typography variant="body2" sx={{ color: '#E0E0E0' }}>{ticket.reporter}</Typography>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <PersonIcon sx={{ color: '#999999', mr: 2 }} />
                  <Box>
                    <Typography variant="caption" sx={{ color: '#999999', display: 'block' }}>Assignee</Typography>
                    <Typography variant="body2" sx={{ color: '#E0E0E0' }}>{ticket.assignee}</Typography>
                  </Box>
                </Box>

                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <AccessTimeIcon sx={{ color: '#999999', mr: 2 }} />
                  <Box>
                    <Typography variant="caption" sx={{ color: '#999999', display: 'block' }}>Created</Typography>
                    <Typography variant="body2" sx={{ color: '#E0E0E0' }}>{ticket.createdAt}</Typography>
                  </Box>
                </Box>

                <Box sx={{ mt: 3 }}>
                  <Typography variant="caption" sx={{ color: '#999999', display: 'block', mb: 1 }}>Support Tier</Typography>
                  <Chip label={ticket.tier} size="small" sx={{ bgcolor: '#5C6BC0', color: '#fff' }} />
                </Box>
              </Paper>
            </Grid>
          </Grid>
        </Paper>
      </Container>
    </Box>
  );
};

export default TicketDetails;
