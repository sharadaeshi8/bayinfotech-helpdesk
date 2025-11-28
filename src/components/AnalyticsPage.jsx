import React from 'react';
import { Box, Paper, Typography, Tabs, Tab, Grid, LinearProgress, Chip, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Card, CardContent } from '@mui/material';
import QueryStatsIcon from '@mui/icons-material/QueryStats';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ScheduleIcon from '@mui/icons-material/Schedule';
import TimerIcon from '@mui/icons-material/Timer';
import PsychologyIcon from '@mui/icons-material/Psychology';
import SelfImprovementIcon from '@mui/icons-material/SelfImprovement';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import { Alert } from '@mui/material';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';
import { Line, Bar, Pie } from 'react-chartjs-2';
import {
  kpiMetrics,
  ticketVolumeTrend,
  predictiveAlert,
  systemPerformance,
  pcteMetrics,
  topIssueCategories,
} from '../data/mockAnalytics';
import {
  frequentQueryTopics,
  resolutionPathMetrics,
  clarificationPatterns,
  chatbotPerformanceMetrics,
  chatbotPredictiveInsights,
  topicSentiments,
  correctivePromptMetrics,
} from '../data/mockChatbotMetrics';
import ChatbotPerformanceMetrics from './ChatbotPerformanceMetrics';
import { fetchMetricsSummary, fetchTrends } from '../api/metrics';

// Register Chart.js once for this screen
ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend, Filler);

// Minimal KPI card used in Overview
const KPICard = ({ metric, icon: Icon }) => {
  const isNegativeMetric = metric.label.includes('Resolution Time') || metric.label.includes('Escalation Rate');
  const isPositive = isNegativeMetric ? metric.trend === 'down' : metric.trend === 'up';
  return (
    <Paper sx={{ p: 2, backgroundColor: '#242424', border: '1px solid #333333', height: '100%' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
        {Icon && <Icon sx={{ fontSize: 24, color: '#D4AF37' }} />}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
          {metric.trend === 'up' ? (
            <TrendingUpIcon sx={{ fontSize: 18, color: isPositive ? '#4A7C59' : '#FF9500' }} />
          ) : (
            <TrendingDownIcon sx={{ fontSize: 18, color: isPositive ? '#4A7C59' : '#FF9500' }} />
          )}
          <Typography variant="caption" sx={{ color: isPositive ? '#4A7C59' : '#FF9500', fontWeight: 'bold' }}>
            {metric.change > 0 ? '+' : ''}{metric.change}%
          </Typography>
        </Box>
      </Box>
      <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 0.5 }}>
        {metric.value.toLocaleString()}{metric.unit || ''}
      </Typography>
      <Typography variant="body2" sx={{ color: '#999999' }}>{metric.label}</Typography>
    </Paper>
  );
};
// Footer metadata chips displayed at the bottom of each tab
const FooterMeta = () => (
  <Box sx={{ mt: 3, p: 2, backgroundColor: '#242424', borderRadius: '8px', border: '1px solid #333333' }}>
    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, flexWrap: 'wrap' }}>
      <Chip label="Real-time" sx={{ backgroundColor: '#2196F3', color: '#1a1a1a', fontWeight: 'bold', height: '32px' }} />
      <Chip label={`Last updated: 2025-01-15 10:00`} sx={{ backgroundColor: '#333333', color: '#E0E0E0', height: '32px' }} />
      <Chip label="Full Analytics - Available Month 18" sx={{ backgroundColor: '#4A7C59', color: '#1a1a1a', fontWeight: 'bold', height: '32px' }} />
    </Box>
  </Box>
);
const AnalyticsPage = () => {
  const [tab, setTab] = React.useState(0);
  // Diagnostic refs for Ticket Volume chart card (Overview tab)
  const tvCardRef = React.useRef(null);
  const tvTitleRef = React.useRef(null);
  const tvPlotRef = React.useRef(null);
  const overviewFooterRef = React.useRef(null);

  React.useEffect(() => {
    const logLayout = () => {
      if (tab !== 0) return;
      const card = tvCardRef.current?.getBoundingClientRect();
      const title = tvTitleRef.current?.getBoundingClientRect();
      const plot = tvPlotRef.current?.getBoundingClientRect();
      const footer = overviewFooterRef.current?.getBoundingClientRect();
      // Compute simple overlap check between plot and footer
      const overlaps = plot && footer ? plot.bottom > footer.top : false;
      const fmt = (name, r) => r
        ? `${name}: top=${r.top.toFixed(1)}, left=${r.left.toFixed(1)}, bottom=${r.bottom.toFixed(1)}, right=${r.right.toFixed(1)}, width=${r.width.toFixed(1)}, height=${r.height.toFixed(1)}`
        : `${name}: null`;
      console.log('[Analytics/Overview/TicketVolume] layout');
      console.log(fmt('card', card));
      console.log(fmt('title', title));
      console.log(fmt('plot', plot));
      console.log(fmt('footer', footer));
      console.log(`overlaps: ${overlaps}`);
      console.log('note: If overlaps=true, plot area extends beyond footer top.');
    };
    logLayout();
    window.addEventListener('resize', logLayout);
    const id = setTimeout(logLayout, 0);
    return () => {
      window.removeEventListener('resize', logLayout);
      clearTimeout(id);
    };
  }, [tab]);

  const [realMetrics, setRealMetrics] = React.useState(null);
  const [ticketTrends, setTicketTrends] = React.useState([]);

  React.useEffect(() => {
    const loadMetrics = async () => {
      try {
        const data = await fetchMetricsSummary();
        setRealMetrics(data);
      } catch (error) {
        console.error("Failed to load metrics", error);
      }
    };
    
    const loadTrends = async () => {
        try {
          const data = await fetchTrends();
          if (data && data.tickets) {
            const formattedTrends = data.tickets.map(t => ({
              time: new Date(t.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
              count: t.count
            }));
            setTicketTrends(formattedTrends);
          }
        } catch (error) {
          console.error("Failed to load trends", error);
        }
      };

    loadMetrics();
    loadTrends();
    // Refresh every 30 seconds
    const interval = setInterval(() => {
        loadMetrics();
        loadTrends();
    }, 30000);
    return () => clearInterval(interval);
  }, []);

  // Merge real metrics with mock metrics
  const displayMetrics = React.useMemo(() => {
    if (!realMetrics) return kpiMetrics;

    return {
      ...kpiMetrics,
      ticketsResolved: {
        ...kpiMetrics.ticketsResolved,
        value: realMetrics.total_conversations || 0,
        label: 'Total Conversations'
      },
      avgResolutionTime: {
        ...kpiMetrics.avgResolutionTime,
        value: realMetrics.average_response_time ? parseFloat(realMetrics.average_response_time.toFixed(2)) : 0,
        unit: 's',
        label: 'Avg Response Time'
      },
      tier0Resolution: {
        ...kpiMetrics.tier0Resolution,
        value: realMetrics.deflection_rate ? parseFloat((realMetrics.deflection_rate * 100).toFixed(1)) : 0,
        label: 'Deflection Rate'
      },
      escalationRate: {
        ...kpiMetrics.escalationRate,
        value: realMetrics.deflection_rate ? parseFloat(((1 - realMetrics.deflection_rate) * 100).toFixed(1)) : 0,
        label: 'Escalation Rate'
      }
    };
  }, [realMetrics]);

  // Derived System Performance
  const realSystemPerf = React.useMemo(() => {
    if (!realMetrics || realMetrics.system_uptime === undefined) return systemPerformance;
    const uptimeDays = (realMetrics.system_uptime / 86400).toFixed(1);
    return {
        ...systemPerformance,
        systemUptime: { ...systemPerformance.systemUptime, value: 99.9, period: `last ${uptimeDays} days` },
        activeConcurrentUsers: {
            ...systemPerformance.activeConcurrentUsers,
            value: realMetrics.active_users || 0,
            percentage: Math.min(100, Math.round(((realMetrics.active_users || 0) / 1000) * 100))
        }
    };
  }, [realMetrics]);

  // Derived Issue Categories
  const realCategories = React.useMemo(() => {
    if (!realMetrics || !realMetrics.tier_distribution) return topIssueCategories;
    const total = Object.values(realMetrics.tier_distribution).reduce((a, b) => a + b, 0);
    if (total === 0) return topIssueCategories;
    
    return [
        { category: 'Access & Auth (Tier 1)', count: realMetrics.tier_distribution['TIER_1'] || 0 },
        { category: 'Infrastructure (Tier 2)', count: realMetrics.tier_distribution['TIER_2'] || 0 },
        { category: 'Critical/Security (Tier 3)', count: realMetrics.tier_distribution['TIER_3'] || 0 },
    ].map(c => ({
        ...c,
        percentage: Math.round((c.count / total) * 100)
    })).sort((a, b) => b.count - a.count);
  }, [realMetrics]);
  // Chart config
  // Chart config
  const lineChartData = React.useMemo(() => ({
    labels: ticketTrends.length > 0 ? ticketTrends.map(d => d.time) : ticketVolumeTrend.map(d => {
      const date = new Date(d.date);
      return `${date.getMonth() + 1}/${date.getDate()}`;
    }),
    datasets: [
      {
        label: 'Ticket Volume',
        data: ticketTrends.length > 0 ? ticketTrends.map(d => d.count) : ticketVolumeTrend.map(d => d.tickets),
        borderColor: '#D4AF37',
        backgroundColor: 'rgba(212, 175, 55, 0.1)',
        fill: true,
        tension: 0.4,
        pointRadius: 2,
      },
    ],
  }), [ticketTrends]);

  // Sentiment Associations (stacked horizontal bar)
  const sentimentBarData = React.useMemo(() => ({
    labels: topicSentiments.map(t => t.topic),
    datasets: [
      { label: 'Frustrated', data: topicSentiments.map(t => t.frustrated), backgroundColor: 'rgba(211,47,47,0.1)', borderColor: '#D32F2F', borderWidth: 2 },
      { label: 'Neutral', data: topicSentiments.map(t => t.neutral), backgroundColor: 'rgba(255,149,0,0.1)', borderColor: '#FF9500', borderWidth: 2 },
      { label: 'Satisfied', data: topicSentiments.map(t => t.satisfied), backgroundColor: 'rgba(74,124,89,0.1)', borderColor: '#4A7C59', borderWidth: 2 },
    ],
  }), []);
  const sentimentBarOptions = React.useMemo(() => ({
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, position: 'top', labels: { color: '#999999', boxWidth: 12, usePointStyle: true } },
      tooltip: { backgroundColor: '#242424', titleColor: '#D4AF37', bodyColor: '#E0E0E0', borderColor: '#333333', borderWidth: 1, padding: 10 },
    },
    scales: {
      x: { stacked: true, grid: { color: '#333333' }, ticks: { color: '#999999' }, title: { display: true, text: 'Count', color: '#999999' } },
      y: { stacked: true, grid: { display: false, drawBorder: false }, ticks: { color: '#999999' }, title: { display: true, text: 'Topic', color: '#999999' } },
    },
  }), []);

  // Corrective Prompts Analysis (pie + summary)
  const correctivePieData = React.useMemo(() => ({
    labels: ['0 Prompts', '1 Prompt', '2 Prompts', '3+ Prompts'],
    datasets: [
      {
        data: [
          correctivePromptMetrics.breakdown.zeroPrompts.count,
          correctivePromptMetrics.breakdown.onePrompt.count,
          correctivePromptMetrics.breakdown.twoPrompts.count,
          correctivePromptMetrics.breakdown.threePlusPrompts.count,
        ],
        backgroundColor: ['#4A7C59', '#D4AF37', '#FF9500', '#FF4444'],
        borderColor: ['#333333', '#333333', '#333333', '#333333'],
        borderWidth: 2,
      },
    ],
  }), []);

  // Issue Categories bar config
  const categoriesBarData = React.useMemo(() => ({
    labels: topIssueCategories.map(c => c.category),
    datasets: [
      {
        label: 'Ticket Count',
        data: topIssueCategories.map(c => c.count),
        backgroundColor: topIssueCategories.map((c, idx) => {
          if (idx === 0) return '#D4AF37';
          if (idx === 1) return '#FF9500';
          if (idx === 2) return '#4A7C59';
          return `rgba(212, 175, 55, ${0.6 - idx * 0.1})`;
        }),
        borderColor: '#333333',
        borderWidth: 1,
      },
    ],
  }), []);
  const categoriesBarOptions = React.useMemo(() => ({
    indexAxis: 'y',
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: true, labels: { color: '#999999', boxWidth: 12, usePointStyle: true } },
      title: { display: false },
      tooltip: {
        backgroundColor: '#242424',
        titleColor: '#D4AF37',
        bodyColor: '#E0E0E0',
        borderColor: '#333333',
        borderWidth: 1,
        padding: 10,
      },
    },
    scales: {
      x: { grid: { color: '#333333' }, ticks: { color: '#999999' }, title: { display: true, text: 'Count', color: '#999999' } },
      y: { grid: { display: false, drawBorder: false }, ticks: { color: '#999999' }, title: { display: true, text: 'Category', color: '#999999' } },
    },
  }), []);
  const lineChartOptions = React.useMemo(() => ({
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: { display: false },
      tooltip: {
        backgroundColor: '#242424',
        titleColor: '#D4AF37',
        bodyColor: '#E0E0E0',
        borderColor: '#333333',
        borderWidth: 1,
        padding: 10,
      },
    },
    scales: {
      x: { grid: { color: '#333333' }, ticks: { color: '#999999' }, title: { display: true, text: 'Date', color: '#999999' } },
      y: { grid: { color: '#333333' }, ticks: { color: '#999999', stepSize: 1, precision: 0 }, title: { display: true, text: 'Tickets', color: '#999999' } },
    },
  }), []);

  return (
    <Box sx={{ p: { xs: 2, sm: 3, md: 4 }, bgcolor: '#1a1a1a', minHeight: '100vh', width: '100%' }}>
      {/* Header Section (match portal style) */}
      <Box sx={{ mb: 4 }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
          <QueryStatsIcon sx={{ fontSize: 40, color: '#D4AF37' }} />
          <Box>
            <Typography variant="h4" sx={{ fontWeight: 'bold', color: '#D4AF37' }}>
              Executive Analytics Dashboard
            </Typography>
            <Typography variant="body1" sx={{ color: '#E0E0E0', mt: 0.5 }}>
              Real-time insights across tickets, chatbot performance, issue categories, and user sentiment
            </Typography>
          </Box>
        </Box>
      </Box>

      <Paper sx={{ backgroundColor: '#242424', border: '1px solid #333333' }}>
        <Tabs
          value={tab}
          onChange={(e, v) => setTab(v)}
          textColor="inherit"
          indicatorColor="secondary"
          variant="scrollable"
          scrollButtons
          allowScrollButtonsMobile
          sx={{
            '& .MuiTabs-indicator': { backgroundColor: '#D4AF37' },
          }}
        >
          <Tab label="Overview" sx={{ color: '#E0E0E0', fontWeight: 'bold', fontSize: { xs: '1rem', md: '1.125rem' } }} />
          <Tab label="Chatbot Analytics" sx={{ color: '#E0E0E0', fontWeight: 'bold', fontSize: { xs: '1rem', md: '1.125rem' } }} />
          <Tab label="Issue Categories" sx={{ color: '#E0E0E0', fontWeight: 'bold', fontSize: { xs: '1rem', md: '1.125rem' } }} />
          <Tab label="User Context & Sentiment" sx={{ color: '#E0E0E0', fontWeight: 'bold', fontSize: { xs: '1rem', md: '1.125rem' } }} />
          <Tab label="Actionable AI Insights" sx={{ color: '#E0E0E0', fontWeight: 'bold', fontSize: { xs: '1rem', md: '1.125rem' } }} />
        </Tabs>
      </Paper>

      {/* Overview Panel */}
      {tab === 0 && (
        <>
          <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold', mt: 3 }}>
            Overview
          </Typography>
          {/* KPI Metrics */}
          <Paper sx={{ mt: 3, mb: 3, p: 3, backgroundColor: '#242424', border: '1px solid #333333', width: '100%' }}>
            <Typography variant="h5" sx={{ mb: 1.5, color: '#D4AF37', fontWeight: 'bold' }}>Key Performance Indicators (KPIs)</Typography>
            <Grid container spacing={2}>
              <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}><KPICard metric={displayMetrics.ticketsResolved} icon={CheckCircleIcon} /></Grid>
              <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}><KPICard metric={displayMetrics.slaCompliance} icon={ScheduleIcon} /></Grid>
              <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}><KPICard metric={displayMetrics.avgResolutionTime} icon={TimerIcon} /></Grid>
              <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}><KPICard metric={displayMetrics.aiAccuracy} icon={PsychologyIcon} /></Grid>
              <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}><KPICard metric={displayMetrics.tier0Resolution} icon={SelfImprovementIcon} /></Grid>
              <Grid size={{ xs: 12, sm: 6, md: 4, lg: 2 }}><KPICard metric={displayMetrics.escalationRate} icon={ArrowDownwardIcon} /></Grid>
            </Grid>
          </Paper>

          {/* Predictive Alert moved to Actionable AI Insights tab */}

          {/* Charts Row */}
          <Grid container spacing={3} sx={{ mb: 4, width: '100%' }} data-testid="charts-grid">
            {/* Ticket Volume Trend */}
            <Grid size={{ xs: 12, lg: 4 }} data-testid="chart-card">
              <Paper ref={tvCardRef} sx={{ p: 3, backgroundColor: '#242424', border: '1px solid #333333', height: '320px', width: '100%', overflow: 'hidden' }}>
                <Typography ref={tvTitleRef} variant="h6" sx={{ mb: 2, color: '#D4AF37', fontWeight: 'bold', fontSize: '1rem' }}>Ticket Volume (24h)</Typography>
                <Box ref={tvPlotRef} sx={{ height: '250px' }}>
                  <Line data={lineChartData} options={lineChartOptions} />
                </Box>
              </Paper>
            </Grid>

            {/* System Performance */}
            <Grid size={{ xs: 12, lg: 4 }} data-testid="chart-card">
              <Paper sx={{ p: 3, backgroundColor: '#242424', border: '1px solid #333333', height: '320px', width: '100%' }}>
                <Typography variant="h6" sx={{ mb: 2, color: '#D4AF37', fontWeight: 'bold', fontSize: '1rem' }}>System Performance</Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Dashboard Load Time</Typography>
                      <Typography variant="body2" sx={{ color: '#4A7C59', fontWeight: 'bold' }}>{realSystemPerf.dashboardLoadTime.value} {realSystemPerf.dashboardLoadTime.unit}</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={(realSystemPerf.dashboardLoadTime.value / realSystemPerf.dashboardLoadTime.threshold) * 100} sx={{ height: 6, backgroundColor: '#333333', '& .MuiLinearProgress-bar': { backgroundColor: '#4A7C59' } }} />
                  </Box>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Data Refresh Interval</Typography>
                      <Typography variant="body2" sx={{ color: '#D4AF37', fontWeight: 'bold' }}>{realSystemPerf.dataRefreshInterval.value} {realSystemPerf.dataRefreshInterval.unit}</Typography>
                    </Box>
                  </Box>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Active Concurrent Users</Typography>
                      <Typography variant="body2" sx={{ color: '#4A7C59', fontWeight: 'bold' }}>
                        {realSystemPerf.activeConcurrentUsers.value} / {realSystemPerf.activeConcurrentUsers.capacity} ({realSystemPerf.activeConcurrentUsers.percentage}%)
                      </Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={realSystemPerf.activeConcurrentUsers.percentage} sx={{ height: 6, backgroundColor: '#333333', '& .MuiLinearProgress-bar': { backgroundColor: realSystemPerf.activeConcurrentUsers.percentage < realSystemPerf.activeConcurrentUsers.threshold ? '#4A7C59' : '#FF9500' } }} />
                  </Box>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" sx={{ color: '#E0E0E0' }}>System Uptime ({realSystemPerf.systemUptime.period})</Typography>
                      <Typography variant="body2" sx={{ color: '#4A7C59', fontWeight: 'bold' }}>{realSystemPerf.systemUptime.value}%</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={realSystemPerf.systemUptime.value} sx={{ height: 6, backgroundColor: '#333333', '& .MuiLinearProgress-bar': { backgroundColor: realSystemPerf.systemUptime.value >= realSystemPerf.systemUptime.threshold ? '#4A7C59' : '#FF9500' } }} />
                  </Box>
                </Box>
              </Paper>
            </Grid>

            {/* Chatbot Performance summary */}
            <Grid size={{ xs: 12, lg: 4 }} data-testid="chart-card">
              <Paper sx={{ p: 3, backgroundColor: '#242424', border: '1px solid #333333', height: '320px', width: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="h6" sx={{ mb: 2, color: '#D4AF37', fontWeight: 'bold', fontSize: '1rem' }}>Chatbot Performance</Typography>
                  <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Resolution Rate</Typography>
                        <Typography variant="body2" sx={{ color: '#4A7C59', fontWeight: 'bold' }}>
                            {realMetrics ? (realMetrics.deflection_rate * 100).toFixed(0) : 74}%
                        </Typography>
                      </Box>
                      <LinearProgress variant="determinate" value={realMetrics ? realMetrics.deflection_rate * 100 : 74} sx={{ height: 6, backgroundColor: '#333333', '& .MuiLinearProgress-bar': { backgroundColor: '#4A7C59' } }} />
                    </Box>
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body2" sx={{ color: '#E0E0E0' }}>User Satisfaction</Typography>
                        <Typography variant="body2" sx={{ color: '#D4AF37', fontWeight: 'bold' }}>4.6/5.0</Typography>
                      </Box>
                      <LinearProgress variant="determinate" value={92} sx={{ height: 6, backgroundColor: '#333333', '& .MuiLinearProgress-bar': { backgroundColor: '#D4AF37' } }} />
                    </Box>
                    <Box>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                        <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Avg Response Time</Typography>
                        <Typography variant="body2" sx={{ color: '#2196F3', fontWeight: 'bold' }}>1.2s</Typography>
                      </Box>
                      <LinearProgress variant="determinate" value={85} sx={{ height: 6, backgroundColor: '#333333', '& .MuiLinearProgress-bar': { backgroundColor: '#2196F3' } }} />
                    </Box>
                  </Box>
                </Box>
              </Paper>
            </Grid>
          </Grid>
          <Box ref={overviewFooterRef}>
            <FooterMeta />
          </Box>
        </>
      )}

      {/* Chatbot Analytics Panel */}
      {tab === 1 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 3 }}>
            Chatbot Analytics & Predictive Insights
          </Typography>

          {/* Chatbot Performance Monitoring */}
          <Paper sx={{ backgroundColor: '#242424', border: '1px solid #333333', mb: 3 }}>
            <Box sx={{ p: 3 }}>
              <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 1.5 }}>
                Chatbot Performance Monitoring
              </Typography>
              <ChatbotPerformanceMetrics chatbotPerformanceMetrics={chatbotPerformanceMetrics} />
            </Box>
          </Paper>

          {/* Frequent Query Topics */}
          <Paper sx={{ p: 3, mb: 3, backgroundColor: '#242424', border: '1px solid #333333' }}>
            <Typography variant="h5" sx={{ mb: 2, color: '#D4AF37', fontWeight: 'bold' }}>
              Frequent Query Topics Analysis
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow sx={{ backgroundColor: '#1a1a1a' }}>
                    <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Topic</TableCell>
                    <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Query Count</TableCell>
                    <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Percentage</TableCell>
                    <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Avg Clarifications</TableCell>
                    <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Resolution Rate</TableCell>
                    <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Avg Response Time</TableCell>
                    <TableCell sx={{ color: '#D4AF37', fontWeight: 'bold' }}>Trend</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {frequentQueryTopics.map((topic, idx) => (
                    <TableRow key={idx} sx={{ backgroundColor: '#242424', '&:hover': { backgroundColor: '#2a2a2a' }, borderBottom: '1px solid #333333' }}>
                      <TableCell sx={{ color: '#E0E0E0', fontWeight: 'bold' }}>{topic.topic}</TableCell>
                      <TableCell sx={{ color: '#E0E0E0' }}>{topic.count}</TableCell>
                      <TableCell sx={{ color: '#999999' }}>{topic.percentage}%</TableCell>
                      <TableCell sx={{ color: '#999999' }}>{topic.avgClarifications}</TableCell>
                      <TableCell>
                        <Chip label={`${topic.resolutionRate}%`} size="small" sx={{ backgroundColor: topic.resolutionRate > 85 ? '#4A7C59' : topic.resolutionRate > 70 ? '#FF9500' : '#FF4444', color: '#ffffff', fontWeight: 'bold' }} />
                      </TableCell>
                      <TableCell sx={{ color: '#999999' }}>{topic.avgResponseTime}s</TableCell>
                      <TableCell>
                        {topic.trend === 'up' ? (
                          <TrendingUpIcon sx={{ color: '#FF9500' }} />
                        ) : topic.trend === 'down' ? (
                          <TrendingDownIcon sx={{ color: '#4A7C59' }} />
                        ) : (
                          <Box sx={{ width: 20, height: 2, backgroundColor: '#999999' }} />
                        )}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>

          {/* Resolution Path Metrics & Clarification Patterns */}
          <Grid container spacing={3} sx={{ mb: 3 }}>
            <Grid size={{ xs: 12, md: 6 }}>
              <Paper sx={{ p: 3, backgroundColor: '#242424', border: '1px solid #333333', height: '100%' }}>
                <Typography variant="h5" sx={{ mb: 2, color: '#D4AF37', fontWeight: 'bold' }}>Resolution Path Metrics</Typography>
                <Typography variant="body2" sx={{ color: '#999999', mb: 2 }}>
                  How often users need additional exchanges before finding resolution (7 days)
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {[
                    ['exchanges1', '1 Exchange'],
                    ['exchanges2', '2 Exchanges'],
                    ['exchanges3', '3 Exchanges'],
                    ['exchanges4Plus', '4+ Exchanges'],
                  ].map(([key, label]) => {
                    const metric = resolutionPathMetrics[key];
                    if (!metric) return null;
                    return (
                      <Box key={key}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="body2" sx={{ color: '#E0E0E0' }}>{label}</Typography>
                          <Typography variant="body2" sx={{ color: '#D4AF37', fontWeight: 'bold' }}>
                            {metric.percentage}% ({metric.count} chats)
                          </Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={metric.percentage}
                          sx={{
                            height: 8,
                            borderRadius: '4px',
                            backgroundColor: '#333333',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor:
                                key === 'exchanges1' ? '#4A7C59' :
                                key === 'exchanges2' ? '#D4AF37' :
                                key === 'exchanges3' ? '#FF9500' : '#FF4444',
                            },
                          }}
                        />
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                          {'avgResolutionTime' in metric && (
                            <Typography variant="caption" sx={{ color: '#666666' }}>Avg Resolution: {metric.avgResolutionTime}s</Typography>
                          )}
                          {'satisfaction' in metric && (
                            <Typography variant="caption" sx={{ color: '#666666' }}>Satisfaction: {metric.satisfaction}/5.0</Typography>
                          )}
                        </Box>
                      </Box>
                    );
                  })}
                  {/* Deflection vs Escalation bars */}
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Deflection rate</Typography>
                      <Typography variant="body2" sx={{ color: '#4A7C59', fontWeight: 'bold' }}>59.5%</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={59.5} sx={{ height: 8, backgroundColor: '#333333', '& .MuiLinearProgress-bar': { backgroundColor: '#4A7C59' } }} />
                  </Box>
                  <Box>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Escalation rate</Typography>
                      <Typography variant="body2" sx={{ color: '#FF4444', fontWeight: 'bold' }}>40.5%</Typography>
                    </Box>
                    <LinearProgress variant="determinate" value={40.5} sx={{ height: 8, backgroundColor: '#333333', '& .MuiLinearProgress-bar': { backgroundColor: '#FF4444' } }} />
                  </Box>
                </Box>
              </Paper>
            </Grid>

            <Grid size={{ xs: 12, md: 6 }}>
              <Paper sx={{ p: 3, backgroundColor: '#242424', border: '1px solid #333333', height: '100%' }}>
                <Typography variant="h5" sx={{ mb: 2, color: '#D4AF37', fontWeight: 'bold' }}>Clarification Patterns</Typography>
                <Typography variant="body2" sx={{ color: '#999999', mb: 1 }}>
                  216 chats were resolved with {'>'}1 exchange (7 days)
                </Typography>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  {clarificationPatterns.map((pattern, idx) => (
                    <Card key={idx} sx={{ backgroundColor: '#1a1a1a', border: '1px solid #333333' }}>
                      <CardContent>
                        <Typography variant="body1" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 1 }}>
                          {pattern.pattern}
                        </Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 1 }}>
                          <Chip label={`${pattern.frequency} chats`} size="small" sx={{ backgroundColor: '#333333', color: '#E0E0E0' }} />
                          <Chip label={`${pattern.percentage}%`} size="small" sx={{ backgroundColor: '#D4AF37', color: '#1a1a1a', fontWeight: 'bold' }} />
                        </Box>
                        <LinearProgress variant="determinate" value={pattern.percentage} sx={{ height: 6, backgroundColor: '#2a2a2a', '& .MuiLinearProgress-bar': { backgroundColor: '#D4AF37' } }} />
                        <Typography variant="caption" sx={{ color: '#666666', display: 'block', mt: 0.5 }}>Common Topics: {pattern.commonTopics.join(', ')}</Typography>
                      </CardContent>
                    </Card>
                  ))}
                </Box>
              </Paper>
            </Grid>
          </Grid>
          <FooterMeta />
        </Box>
      )}

      {/* Actionable AI Insights Panel */}
      {tab === 4 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 3 }}>
            Actionable AI Insights
          </Typography>

          {/* Predictive Alert */}
          <Alert
            severity="warning"
            sx={{ mb: 3, backgroundColor: '#2A2417', border: '1px solid #FF9500', color: '#E0E0E0', '& .MuiAlert-icon': { color: '#FF9500' } }}
          >
            <Typography variant="body1" sx={{ fontWeight: 'bold', mb: 0.5 }}>
              Predictive Alert: {predictiveAlert.message}
            </Typography>
            <Typography variant="body2" sx={{ color: '#999999', mb: 1 }}>
              A significant increase in ticket volume is forecasted before an upcoming training event.
            </Typography>
            <Typography variant="caption" sx={{ color: '#666666', display: 'block', mb: 1 }}>
              Forecast Date: {predictiveAlert.forecastDate} | Confidence: {predictiveAlert.confidence}%
            </Typography>
            <Typography variant="body2" sx={{ color: '#D4AF37', fontWeight: 'bold', mt: 1 }}>
              Recommended Action: {predictiveAlert.recommendedAction}
            </Typography>
          </Alert>

          {/* Chatbot Predictive Insights (3 boxes) */}
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2, mb: 3 }}>
            {chatbotPredictiveInsights.map((insight, idx) => (
              <Alert
                key={idx}
                severity={insight.severity === 'warning' ? 'warning' : insight.severity === 'success' ? 'success' : 'info'}
                sx={{
                  backgroundColor:
                    insight.severity === 'warning' ? '#2A2417' :
                    insight.severity === 'success' ? '#1F2A24' : '#1E2A32',
                  border: `1px solid ${insight.severity === 'warning' ? '#FF9500' : insight.severity === 'success' ? '#4A7C59' : '#2196F3'}`,
                  color: '#E0E0E0',
                  '& .MuiAlert-icon': {
                    color: insight.severity === 'warning' ? '#FF9500' :
                           insight.severity === 'success' ? '#4A7C59' : '#2196F3',
                  },
                }}
              >
                <Typography variant="body1" sx={{ fontWeight: 'bold', mb: 0.5 }}>
                  {insight.type === 'spike_prediction' ? '📈 Predictive Alert' :
                   insight.type === 'knowledge_gap' ? '📚 Knowledge Gap Detected' :
                   insight.type === 'escalation_risk' ? '⚠️ Escalation Risk Detected' :
                   '✅ Accuracy Trend'}
                </Typography>
                <Typography variant="body2" sx={{ color: '#999999', mb: 1 }}>{insight.message}</Typography>
                <Typography variant="caption" sx={{ color: '#666666', display: 'block', mb: 1 }}>
                  {insight.window ? `Time Period: ${insight.window} | ` : ''}Confidence: {insight.confidence}%
                </Typography>
                <Typography variant="body2" sx={{ color: '#D4AF37', fontWeight: 'bold', mt: 1 }}>
                  Recommended Action: {insight.recommendedAction}
                </Typography>
              </Alert>
            ))}
          </Box>

          {/* Anomaly Detection Alert */}
          <Alert
            severity="info"
            sx={{ backgroundColor: '#1E2A32', border: '1px solid #2196F3', color: '#E0E0E0', '& .MuiAlert-icon': { color: '#2196F3' } }}
          >
            <Typography variant="body1" sx={{ fontWeight: 'bold', mb: 0.5 }}>
              Anomaly Detected: Unusual spike in tickets on 10/28
            </Typography>
            <Typography variant="body2" sx={{ color: '#999999', mb: 1 }}>
              An unusual spike in ticket volume was detected on October 28th, requiring investigation.
            </Typography>
            <Typography variant="caption" sx={{ color: '#666666', display: 'block', mb: 1 }}>
              Detection Date: October 28th | Confidence: 89%
            </Typography>
            <Typography variant="body2" sx={{ color: '#D4AF37', fontWeight: 'bold', mt: 1 }}>
              Recommended Action: Review KB articles for "Lab Access" and schedule proactive communications.
            </Typography>
          </Alert>

          <FooterMeta />
        </Box>
      )}

      {/* Issue Categories Panel */}
      {tab === 2 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 3 }}>
            Issue Categories & Trends
          </Typography>
          {/* Top Issue Categories Chart */}
          <Paper sx={{ p: 3, backgroundColor: '#242424', border: '1px solid #333333', height: '400px' }}>
            <Typography variant="h6" sx={{ mb: 2, color: '#D4AF37', fontWeight: 'bold', fontSize: '1rem' }}>Top Issue Categories</Typography>
            <Box sx={{ height: '300px' }}>
              <Bar data={categoriesBarData} options={categoriesBarOptions} />
            </Box>
          </Paper>

          {/* Issue Categories Heatmap (visual density strip) */}
          <Paper sx={{ mt: 3, p: 3, backgroundColor: '#242424', border: '1px solid #333333' }}>
            <Typography variant="h5" sx={{ mb: 2, color: '#D4AF37', fontWeight: 'bold' }}>Top Issue Categories Heatmap</Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {realCategories.map((c, idx) => {
                const intensity = Math.min(1, Math.max(0.2, c.percentage / 30));
                const bg = `rgba(212, 175, 55, ${intensity})`;
                const darkText = intensity > 0.6;
                return (
                  <Box key={idx} sx={{ minWidth: '140px', px: 2, py: 1.5, backgroundColor: bg, border: '1px solid #333333', borderRadius: '4px' }}>
                    <Typography variant="body2" sx={{ color: darkText ? '#1a1a1a' : '#E0E0E0', fontWeight: 'bold' }}>{c.category}</Typography>
                    <Typography variant="caption" sx={{ color: darkText ? '#1a1a1a' : '#E0E0E0' }}>{c.count} ({c.percentage}%)</Typography>
                  </Box>
                );
              })}
            </Box>
            <Typography variant="caption" sx={{ display: 'block', mt: 1, color: '#999999' }}>
              Darker gold indicates higher concentration of issues.
            </Typography>
          </Paper>

          {/* Anomaly Detection Alert moved to Actionable AI Insights tab */}
          <FooterMeta />
        </Box>
      )}

      {/* User Context & Sentiment Panel */}
      {tab === 3 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 3 }}>
            User Context & Sentiment
          </Typography>
          {/* Sentiment Associations with Topics */}
          <Paper sx={{ backgroundColor: '#242424', border: '1px solid #333333', mb: 3 }}>
            <Box sx={{ p: 3 }}>
              <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 2 }}>
                Sentiment Associations with Topics
              </Typography>
              <Box sx={{ height: '400px' }}>
                <Bar data={sentimentBarData} options={sentimentBarOptions} />
              </Box>
            </Box>
          </Paper>

          {/* User Context/Corrective Prompts Metrics */}
          <Paper sx={{ backgroundColor: '#242424', border: '1px solid #333333', mb: 3 }}>
            <Box sx={{ p: 3 }}>
              <Typography variant="h5" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 2 }}>
                User Context & Corrective Prompts Analysis
              </Typography>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Box sx={{ height: '300px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <Pie data={correctivePieData} options={{ responsive: true, maintainAspectRatio: true, plugins: { legend: { position: 'bottom', labels: { color: '#999999', usePointStyle: true } } } }} />
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Paper sx={{ backgroundColor: '#1a1a1a', border: '1px solid #333333', height: '100%' }}>
                    <Box sx={{ p: 2 }}>
                      <Typography variant="h6" sx={{ color: '#D4AF37', fontWeight: 'bold', mb: 2 }}>Metrics Summary</Typography>
                      <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Total Queries Analyzed</Typography>
                          <Typography variant="body2" sx={{ color: '#D4AF37', fontWeight: 'bold' }}>{correctivePromptMetrics.totalQueries.toLocaleString()}</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Queries Needing Context</Typography>
                          <Typography variant="body2" sx={{ color: '#FF9500', fontWeight: 'bold' }}>{correctivePromptMetrics.queriesNeedingContext} ({((correctivePromptMetrics.queriesNeedingContext / correctivePromptMetrics.totalQueries) * 100).toFixed(1)}%)</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Queries Needing Correction</Typography>
                          <Typography variant="body2" sx={{ color: '#FF4444', fontWeight: 'bold' }}>{correctivePromptMetrics.queriesNeedingCorrection} ({((correctivePromptMetrics.queriesNeedingCorrection / correctivePromptMetrics.totalQueries) * 100).toFixed(1)}%)</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Avg Context Prompts per Query</Typography>
                          <Typography variant="body2" sx={{ color: '#D4AF37', fontWeight: 'bold' }}>{correctivePromptMetrics.avgContextPrompts}</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                          <Typography variant="body2" sx={{ color: '#E0E0E0' }}>Avg Correction Prompts per Query</Typography>
                          <Typography variant="body2" sx={{ color: '#D4AF37', fontWeight: 'bold' }}>{correctivePromptMetrics.avgCorrectionPrompts}</Typography>
                        </Box>
                      </Box>
                    </Box>
                  </Paper>
                </Grid>
              </Grid>
            </Box>
          </Paper>
          <FooterMeta />
        </Box>
      )}
    </Box>
  );
};

export default AnalyticsPage;
