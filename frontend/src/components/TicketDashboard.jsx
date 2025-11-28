import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Chip,
  Grid,
  LinearProgress,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Tooltip,
} from '@mui/material';
import JiraIcon from '@mui/icons-material/IntegrationInstructions';
import TagIcon from '@mui/icons-material/Label';
import SentimentIcon from '@mui/icons-material/EmojiEmotions';
import ConfirmationNumberIcon from '@mui/icons-material/ConfirmationNumber';
import { getTickets } from '../api/ticket';
import { useEffect } from 'react';

import { useLocation } from 'react-router-dom';

const TicketDashboard = () => {
  const location = useLocation();
  const queryParams = new URLSearchParams(location.search);
  const ticketIdParam = queryParams.get('id');

  const [filterTier, setFilterTier] = useState('All');
  const [filterStatus, setFilterStatus] = useState('All');
  const [filterPriority, setFilterPriority] = useState('All');
  const [tickets, setTickets] = useState([
    {
      id: 'JIRA-5421',
      title: 'Cannot access training lab environment',
      status: 'Open',
      priority: 'High',
      tier: 'Tier 1',
      tags: [
        { label: 'Access Control', confidence: 94 },
        { label: 'Lab Environment', confidence: 91 },
      ],
      sentiment: 'Frustrated',
      sentimentScore: 0.78,
      kbMatch: 'KB-2024-001 (89%)',
      slaRisk: true,
      createdAt: '2025-01-15 09:23',
    },
    {
      id: 'JIRA-5420',
      title: 'Password reset not working',
      status: 'Open',
      priority: 'Medium',
      tier: 'Tier 0',
      tags: [
        { label: 'Authentication', confidence: 96 },
        { label: 'Account Management', confidence: 88 },
      ],
      sentiment: 'Neutral',
      sentimentScore: 0.45,
      kbMatch: 'KB-2024-003 (92%)',
      slaRisk: false,
      createdAt: '2025-01-15 08:45',
    },
    {
      id: 'JIRA-5419',
      title: 'Dashboard performance degradation',
      status: 'In Progress',
      priority: 'High',
      tier: 'Tier 2',
      tags: [
        { label: 'Performance', confidence: 93 },
        { label: 'Infrastructure', confidence: 85 },
      ],
      sentiment: 'Neutral',
      sentimentScore: 0.52,
      kbMatch: 'KB-2024-012 (76%)',
      slaRisk: true,
      createdAt: '2025-01-15 07:12',
    },
    {
      id: 'JIRA-5418',
      title: 'Mattermost integration not syncing',
      status: 'Open',
      priority: 'Critical',
      tier: 'Tier 2',
      tags: [
        { label: 'Integration', confidence: 97 },
        { label: 'Mattermost', confidence: 94 },
      ],
      sentiment: 'Frustrated',
      sentimentScore: 0.82,
      kbMatch: 'KB-2024-008 (87%)',
      slaRisk: true,
      createdAt: '2025-01-15 06:30',
    },
    {
      id: 'JIRA-5417',
      title: 'How to configure SSO?',
      status: 'Resolved',
      priority: 'Low',
      tier: 'Tier 0',
      tags: [
        { label: 'Configuration', confidence: 92 },
        { label: 'Security', confidence: 89 },
      ],
      sentiment: 'Satisfied',
      sentimentScore: 0.25,
      kbMatch: 'KB-2024-015 (95%)',
      slaRisk: false,
      createdAt: '2025-01-14 15:22',
    },
    {
      id: 'JIRA-5416',
      title: 'Ticket export to CSV failing',
      status: 'Open',
      priority: 'Medium',
      tier: 'Tier 1',
      tags: [
        { label: 'Export', confidence: 91 },
        { label: 'Data Management', confidence: 86 },
      ],
      sentiment: 'Neutral',
      sentimentScore: 0.48,
      kbMatch: 'KB-2024-005 (84%)',
      slaRisk: false,
      createdAt: '2025-01-15 05:18',
    },
  ]);

  useEffect(() => {
    const fetchTickets = async () => {
      try {
        const realTickets = await getTickets();
        if (realTickets && realTickets.length > 0) {
          // Prepend real tickets to mock tickets
          setTickets(prev => {
            // Filter out any real tickets that might already be in state (if we were polling)
            // But for now just prepend.
            // Map backend fields to frontend format if necessary
            const formattedTickets = realTickets.map(t => ({
              ...t,
              // Ensure tags are in correct format if backend differs
              tags: t.tags || [],
              // Format date
              createdAt: new Date(t.created_at).toLocaleString('en-US', { 
                year: 'numeric', month: '2-digit', day: '2-digit', 
                hour: '2-digit', minute: '2-digit', hour12: false 
              }).replace(',', '')
            }));
            
            // Combine, putting new real tickets first
            return [...formattedTickets, ...prev];
          });
        }
      } catch (error) {
        console.error("Failed to fetch tickets:", error);
      }
    };
    
    fetchTickets();
    // Poll every 10 seconds
    const interval = setInterval(fetchTickets, 10000);
    return () => clearInterval(interval);
  }, []);

  const filteredTickets = tickets.filter((ticket) => {
    if (filterTier !== 'All' && ticket.tier !== filterTier) return false;
    if (filterStatus !== 'All' && ticket.status !== filterStatus) return false;
    if (filterPriority !== 'All' && ticket.priority !== filterPriority) return false;
    // If ticketIdParam is present, only show that ticket
    if (ticketIdParam && ticket.id !== ticketIdParam) return false;
    return true;
  });

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'Critical':
        return '#D32F2F';
      case 'High':
        return '#FF9500';
      case 'Medium':
        return '#FBC02D';
      case 'Low':
        return '#4A7C59';
      default:
        return '#999999';
    }
  };

  const getSentimentColor = (sentiment) => {
    switch (sentiment) {
      case 'Frustrated':
        return '#D32F2F';
      case 'Neutral':
        return '#FF9500';
      case 'Satisfied':
        return '#4A7C59';
      default:
        return '#999999';
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Open':
        return '#FF9500';
      case 'In Progress':
        return '#2196F3';
      case 'Resolved':
        return '#4A7C59';
      default:
        return '#999999';
    }
  };

  // Calculate statistics
  const totalTickets = tickets.length;
  
  const tier0Tickets = tickets.filter(t => t.tier === 'Tier 0').length;
  const tier0Rate = totalTickets > 0 ? Math.round((tier0Tickets / totalTickets) * 100) : 0;
  
  const frustratedCount = tickets.filter(t => t.sentiment === 'Frustrated').length;
  const neutralCount = tickets.filter(t => t.sentiment === 'Neutral').length;
  const satisfiedCount = tickets.filter(t => t.sentiment === 'Satisfied').length;
  
  const frustratedPct = totalTickets > 0 ? Math.round((frustratedCount / totalTickets) * 100) : 0;
  const neutralPct = totalTickets > 0 ? Math.round((neutralCount / totalTickets) * 100) : 0;
  const satisfiedPct = totalTickets > 0 ? Math.round((satisfiedCount / totalTickets) * 100) : 0;
  
  const ticketsAtRisk = tickets.filter(t => t.slaRisk).length;
  
  const tier1Tickets = tickets.filter(t => t.tier === 'Tier 1').length;
  const tier2Tickets = tickets.filter(t => t.tier === 'Tier 2').length;
  
  const tier1Pct = totalTickets > 0 ? Math.round((tier1Tickets / totalTickets) * 100) : 0;
  const tier2Pct = totalTickets > 0 ? Math.round((tier2Tickets / totalTickets) * 100) : 0;

  return (
    <Box sx={{ p: { xs: 2, sm: 3, md: 4 }, bgcolor: '#1a1a1a', minHeight: '100vh', width: '100%' }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2 }}>
          <ConfirmationNumberIcon sx={{ fontSize: 40, color: '#D4AF37' }} />
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#D4AF37' }}>
              Help Desk Ticket Dashboard
            </Typography>
            <Typography variant="body1" sx={{ color: '#E0E0E0', mt: 0.5 }}>
              AI-enriched ticket management with auto-tagging, sentiment analysis, and KB recommendations
            </Typography>
          </Box>
        </Box>
      </Box>

      {/* Overall Tickets Statistics Section */}
      <Paper
        sx={{
          p: 3,
          mb: 4,
          backgroundColor: '#242424',
          border: '1px solid #333333',
          width: '100%',
        }}
      >
        <Typography variant="h3" sx={{ mb: 3, color: '#D4AF37', fontWeight: 'bold' }}>
          Overall Tickets Statistics
        </Typography>
        <Grid container spacing={3}>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, backgroundColor: '#1a1a1a', borderLeft: '4px solid #D4AF37' }}>
              <Typography variant="caption" sx={{ color: '#999999' }}>
                Total Tickets
              </Typography>
              <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold' }}>
                {totalTickets}
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, backgroundColor: '#1a1a1a', borderLeft: '4px solid #4A7C59' }}>
              <Typography variant="caption" sx={{ color: '#999999' }}>
                Tier 0 Resolution Rate
              </Typography>
              <Typography variant="h5" sx={{ color: '#4A7C59', fontWeight: 'bold' }}>
                {tier0Rate}%
              </Typography>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, backgroundColor: '#1a1a1a', borderLeft: '4px solid #2196F3' }}>
              <Typography variant="caption" sx={{ color: '#999999', mb: 1.5, display: 'block' }}>
                Customer Sentiment
              </Typography>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                <Chip
                  label={`${frustratedPct}% Frustrated`}
                  size="small"
                  sx={{
                    backgroundColor: '#D32F2F',
                    color: '#ffffff',
                    fontSize: '0.7rem',
                    height: '20px',
                    fontWeight: 'bold',
                  }}
                />
                <Chip
                  label={`${neutralPct}% Neutral`}
                  size="small"
                  sx={{
                    backgroundColor: '#FF9500',
                    color: '#ffffff',
                    fontSize: '0.7rem',
                    height: '20px',
                    fontWeight: 'bold',
                  }}
                />
                <Chip
                  label={`${satisfiedPct}% Satisfied`}
                  size="small"
                  sx={{
                    backgroundColor: '#4A7C59',
                    color: '#ffffff',
                    fontSize: '0.7rem',
                    height: '20px',
                    fontWeight: 'bold',
                  }}
                />
              </Box>
            </Paper>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Tooltip title="Tickets approaching their SLA deadline without resolution" arrow>
              <Paper sx={{ p: 2, backgroundColor: '#1a1a1a', borderLeft: '4px solid #FF9500', cursor: 'help' }}>
                <Typography variant="caption" sx={{ color: '#999999', display: 'block', mb: 0.5 }}>
                  Tickets at Risk
                </Typography>
                <Typography variant="h5" sx={{ color: '#FF9500', fontWeight: 'bold' }}>
                  {ticketsAtRisk}
                </Typography>
              </Paper>
            </Tooltip>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <Paper sx={{ p: 2, backgroundColor: '#1a1a1a', borderLeft: '4px solid #2196F3' }}>
              <Typography variant="caption" sx={{ color: '#999999', mb: 1.5, display: 'block' }}>
                Tickets by Tier
              </Typography>
              <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                <Chip
                  label={`Tier 0: ${tier0Rate}%`}
                  size="small"
                  sx={{
                    backgroundColor: '#4A7C59',
                    color: '#ffffff',
                    fontSize: '0.7rem',
                    height: '20px',
                    fontWeight: 'bold',
                  }}
                />
                <Chip
                  label={`Tier 1: ${tier1Pct}%`}
                  size="small"
                  sx={{
                    backgroundColor: '#2196F3',
                    color: '#ffffff',
                    fontSize: '0.7rem',
                    height: '20px',
                    fontWeight: 'bold',
                  }}
                />
                <Chip
                  label={`Tier 2: ${tier2Pct}%`}
                  size="small"
                  sx={{
                    backgroundColor: '#D4AF37',
                    color: '#1a1a1a',
                    fontSize: '0.7rem',
                    height: '20px',
                    fontWeight: 'bold',
                  }}
                />
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Paper>

      {/* Filters */}
      <Paper sx={{ p: 3, backgroundColor: '#242424', mb: 3 }}>
        <Typography variant="subtitle2" sx={{ mb: 2, color: '#D4AF37', fontWeight: 'bold' }}>
          Filters
        </Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: '#999999' }}>Tier</InputLabel>
              <Select
                value={filterTier}
                onChange={(e) => setFilterTier(e.target.value)}
                label="Tier"
                sx={{
                  backgroundColor: '#1a1a1a',
                  color: '#ffffff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#333333' },
                }}
              >
                <MenuItem value="All">All Tiers</MenuItem>
                <MenuItem value="Tier 0">Tier 0</MenuItem>
                <MenuItem value="Tier 1">Tier 1</MenuItem>
                <MenuItem value="Tier 2">Tier 2</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: '#999999' }}>Status</InputLabel>
              <Select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                label="Status"
                sx={{
                  backgroundColor: '#1a1a1a',
                  color: '#ffffff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#333333' },
                }}
              >
                <MenuItem value="All">All Statuses</MenuItem>
                <MenuItem value="Open">Open</MenuItem>
                <MenuItem value="In Progress">In Progress</MenuItem>
                <MenuItem value="Resolved">Resolved</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel sx={{ color: '#999999' }}>Priority</InputLabel>
              <Select
                value={filterPriority}
                onChange={(e) => setFilterPriority(e.target.value)}
                label="Priority"
                sx={{
                  backgroundColor: '#1a1a1a',
                  color: '#ffffff',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#333333' },
                }}
              >
                <MenuItem value="All">All Priorities</MenuItem>
                <MenuItem value="Critical">Critical</MenuItem>
                <MenuItem value="High">High</MenuItem>
                <MenuItem value="Medium">Medium</MenuItem>
                <MenuItem value="Low">Low</MenuItem>
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      {/* Tickets Table */}
      <TableContainer component={Paper} sx={{ backgroundColor: '#242424' }}>
        <Table>
          <TableHead>
            <TableRow sx={{ backgroundColor: '#1a1a1a' }}>
              <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Ticket ID</TableCell>
              <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Title</TableCell>
              <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Priority</TableCell>
              <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Status</TableCell>
              <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Tier</TableCell>
              <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>AI Tags</TableCell>
              <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Sentiment</TableCell>
              <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>KB Match</TableCell>
              <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>SLA</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {filteredTickets.map((ticket) => (
              <TableRow
                key={ticket.id}
                sx={{
                  backgroundColor: '#242424',
                  '&:hover': { backgroundColor: '#2a2a2a' },
                  borderBottom: '1px solid #333333',
                }}
              >
                <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <JiraIcon sx={{ fontSize: '16px', color: '#0052CC' }} />
                    <Box
                      component="span"
                      onClick={() => {
                        // Handle ticket click - could navigate to ticket details or copy to clipboard
                        navigator.clipboard?.writeText(ticket.id);
                      }}
                      sx={{
                        cursor: 'pointer',
                        textDecoration: 'underline',
                        '&:hover': {
                          color: '#FFD700',
                        },
                      }}
                    >
                      {ticket.id}
                    </Box>
                  </Box>
                </TableCell>
                <TableCell sx={{ color: '#ffffff', maxWidth: '200px' }}>
                  <Typography variant="body2">{ticket.title}</Typography>
                  <Typography variant="caption" sx={{ color: '#999999' }}>
                    {ticket.createdAt}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Chip
                    label={ticket.priority}
                    size="small"
                    sx={{
                      backgroundColor: getPriorityColor(ticket.priority),
                      color: '#ffffff',
                      fontWeight: 'bold',
                    }}
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={ticket.status}
                    size="small"
                    sx={{
                      backgroundColor: getStatusColor(ticket.status),
                      color: '#ffffff',
                      fontWeight: 'bold',
                    }}
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="caption" sx={{ color: '#D4AF37', fontWeight: 'bold' }}>
                    {ticket.tier}
                  </Typography>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                    {ticket.tags.map((tag, idx) => (
                      <Chip
                        key={idx}
                        icon={<TagIcon />}
                        label={`${tag.label} (${tag.confidence}%)`}
                        size="small"
                        sx={{
                          backgroundColor: '#333333',
                          color: '#D4AF37',
                          fontSize: '11px',
                        }}
                      />
                    ))}
                  </Box>
                </TableCell>
                <TableCell>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <SentimentIcon
                      sx={{
                        fontSize: '16px',
                        color: getSentimentColor(ticket.sentiment),
                      }}
                    />
                    <Typography variant="caption" sx={{ color: '#ffffff' }}>
                      {ticket.sentiment}
                    </Typography>
                  </Box>
                </TableCell>
                <TableCell>
                  <Typography variant="caption" sx={{ color: '#4A7C59' }}>
                    {ticket.kbMatch}
                  </Typography>
                </TableCell>
                <TableCell>
                  {ticket.slaRisk ? (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          backgroundColor: '#FF9500',
                        }}
                      />
                      <Typography variant="caption" sx={{ color: '#FF9500' }}>
                        At Risk
                      </Typography>
                    </Box>
                  ) : (
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Box
                        sx={{
                          width: '8px',
                          height: '8px',
                          borderRadius: '50%',
                          backgroundColor: '#4A7C59',
                        }}
                      />
                      <Typography variant="caption" sx={{ color: '#4A7C59' }}>
                        OK
                      </Typography>
                    </Box>
                  )}
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Footer Note */}
      <Box sx={{ mt: 3, p: 2, backgroundColor: '#242424', borderRadius: '8px', border: '1px solid #333333' }}>
        <Typography variant="caption" sx={{ color: '#999999' }}>
          <strong>AI-Enriched Data:</strong> Tags, sentiment, and KB recommendations are generated by the AI system. All confidence scores reflect model certainty. SLA risk is calculated based on ticket age and priority.
        </Typography>
      </Box>
    </Box>
  );
};

export default TicketDashboard;
