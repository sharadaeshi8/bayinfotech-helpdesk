// AIChatPanel - Main chat interface component
import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box,
  Typography,
  IconButton,
  Alert,
  CircularProgress,
  Collapse,
  Chip,
  Paper,
  alpha,
} from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import ExpandLessIcon from '@mui/icons-material/ExpandLess';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import ChatIcon from '@mui/icons-material/Chat';
import { styled } from '@mui/material/styles';
import ChatMessage from './ChatMessage';
import ChatInput from './ChatInput';
import { simulateTypingDelay, shouldCreateTicket } from '../utils/aiSimulatorSimple';

import { generateTicketData, createTicket } from '../api/ticket';
import { sendMessageToBackend, mapRoleToBackend } from '../api/chat';
import { useAuth } from '../context/AuthContext';

const ChatPanel = styled(Paper)(({ theme }) => ({
  position: 'fixed',
  bottom: 24,
  right: 24,
  width: '420px',
  height: 'calc(100vh - 112px)',
  maxHeight: '700px',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: '#1a1a1a',
  color: '#E0E0E0',
  borderRadius: '16px',
  border: `2px solid ${alpha('#D4AF37', 0.3)}`,
  boxShadow: '0 8px 32px rgba(0, 0, 0, 0.6), 0 4px 16px rgba(212, 175, 55, 0.2)',
  zIndex: 1000,
  background: `linear-gradient(180deg, ${alpha('#1a1a1a', 1)} 0%, ${alpha('#121212', 1)} 100%)`,
  overflow: 'hidden',
  [theme.breakpoints.down('lg')]: {
    width: '380px',
  },
  [theme.breakpoints.down('md')]: {
    width: 'calc(100vw - 48px)',
    right: 24,
    left: 24,
    height: 'calc(100vh - 112px)',
    maxHeight: '85vh',
  },
}));

const ChatHeader = styled(Box)(({ theme }) => ({
  padding: '20px 24px',
  borderBottom: `2px solid ${alpha('#D4AF37', 0.2)}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  background: `linear-gradient(135deg, ${alpha('#D4AF37', 0.15)} 0%, ${alpha('#0052CC', 0.1)} 100%)`,
  borderRadius: '16px 16px 0 0',
  position: 'relative',
  '&::after': {
    content: '""',
    position: 'absolute',
    bottom: 0,
    left: 0,
    right: 0,
    height: '2px',
    background: `linear-gradient(90deg, transparent, ${alpha('#D4AF37', 0.6)}, transparent)`,
  },
}));

const MessagesContainer = styled(Box)(({ theme }) => ({
  flex: 1,
  overflowY: 'auto',
  padding: '20px',
  background: `linear-gradient(180deg, ${alpha('#1a1a1a', 1)} 0%, ${alpha('#121212', 1)} 100%)`,
  '&::-webkit-scrollbar': {
    width: '10px',
  },
  '&::-webkit-scrollbar-track': {
    backgroundColor: '#121212',
    borderRadius: '5px',
  },
  '&::-webkit-scrollbar-thumb': {
    backgroundColor: alpha('#D4AF37', 0.3),
    borderRadius: '5px',
    border: '2px solid #121212',
    '&:hover': {
      backgroundColor: alpha('#D4AF37', 0.5),
    },
  },
}));

const TypingIndicator = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: '10px',
  padding: '12px 16px',
  color: '#999999',
  backgroundColor: alpha('#333333', 0.3),
  borderRadius: '12px',
  border: `1px solid ${alpha('#D4AF37', 0.2)}`,
  marginBottom: '12px',
  width: 'fit-content',
}));

const AIChatPanel = ({ isOpen, onClose, onTicketCreated, initialMessage = null }) => {
  const { user } = useAuth();
  const [messages, setMessages] = useState([]);
  const [isTyping, setIsTyping] = useState(false);
  const [typingMessage, setTypingMessage] = useState('Understanding request...');
  const [conversationContext, setConversationContext] = useState({});
  const [escalationStatus, setEscalationStatus] = useState(null);
  const [isAgentActive, setIsAgentActive] = useState(false);
  const [collapsed, setCollapsed] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const typingIntervalRef = useRef(null);
  const initialMessageSentRef = useRef(false);
  const lastInitialMessageRef = useRef(null);

  // Rotating typing messages
  const typingMessages = [
    'Understanding request...',
    'Analyzing...',
    'Processing...',
    'Generating response...',
  ];

  // Rotate typing messages when typing
  useEffect(() => {
    if (isTyping && !escalationStatus) {
      let messageIndex = 0;
      setTypingMessage(typingMessages[0]);
      
      typingIntervalRef.current = setInterval(() => {
        messageIndex = (messageIndex + 1) % typingMessages.length;
        setTypingMessage(typingMessages[messageIndex]);
      }, 1500);
      
      return () => {
        if (typingIntervalRef.current) {
          clearInterval(typingIntervalRef.current);
        }
      };
    } else {
      if (typingIntervalRef.current) {
        clearInterval(typingIntervalRef.current);
      }
    }
  }, [isTyping, escalationStatus]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  // Initialize with welcome message when chat is opened and not collapsed
  useEffect(() => {
    if (isOpen && !collapsed) {
      // Only initialize welcome message if messages array is empty
      if (messages.length === 0) {
        const welcomeMessage = {
          id: Date.now(),
          type: 'ai',
          content: "Hello! I'm your AI assistant for PCTE Help Desk. How can I help you today?",
          timestamp: new Date(),
          sentiment: { sentiment: 'neutral', score: 0 },
          confidence: 0.95,
        };
        setMessages([welcomeMessage]);
      }
    }
  }, [isOpen, collapsed, messages.length]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = useCallback(async (userMessage) => {
    // Add user message
    const userMsg = {
      id: Date.now(),
      type: 'user',
      content: userMessage,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMsg]);

    const updatedHistory = [...messages, userMsg];
    
    // Check if we're waiting for ticket details
    if (conversationContext.waitingForTicketDetails) {
      // User provided ticket details - AI Agent creates ticket autonomously with cool animation
      const ticketData = await generateTicketData(updatedHistory, userMessage);
      ticketData.description = userMessage; // Use detailed message
      ticketData.subject = `Lab Crash - ${userMessage.substring(0, 50)}...`;
      
      setIsTyping(true);
      
      // Show analyzing
      const analyzingMsg = {
        id: Date.now() + 0.1,
        type: 'ai',
        content: '🔍 Analyzing request...',
        timestamp: new Date(),
        isAnalyzing: true,
      };
      setMessages(prev => [...prev, analyzingMsg]);
      
      await new Promise(resolve => setTimeout(resolve, 800));
      setMessages(prev => prev.filter(msg => !msg.isAnalyzing));
      
      // Show AI Agent processing ticket creation with cool animation
      const processingMsg = {
        id: Date.now() + 0.2,
        type: 'ai',
        content: '🤖 **AI Agent Processing Ticket Creation...**\n\n📋 Analyzing details...\n🔍 Classifying priority...\n📝 Generating ticket...',
        timestamp: new Date(),
        isProcessing: true,
      };
      setMessages(prev => [...prev, processingMsg]);
      
      // Show processing message for 3 seconds (user can see it)
      await new Promise(resolve => setTimeout(resolve, 3000));
      
      // Keep processing message but mark it as done
      setMessages(prev => prev.map(msg => 
        msg.id === processingMsg.id ? { ...msg, isProcessing: false } : msg
      ));
      
      // Show ticket created with typing effect
      const ticketMsg = {
        id: Date.now() + 1,
        type: 'ai',
        content: `✅ **Support ticket ${ticketData.id} has been created successfully!**\n\n**Ticket Details:**\n- **ID:** ${ticketData.id}\n- **Priority:** ${ticketData.priority}\n- **Status:** ${ticketData.status}\n- **Description:** ${userMessage.substring(0, 100)}${userMessage.length > 100 ? '...' : ''}\n\n**View Ticket:** [Open Ticket ${ticketData.id}](/ticket/${ticketData.id})\n\nOur support team will review your ticket and get back to you within 2 hours.`,
        timestamp: new Date(),
        sentiment: { sentiment: 'neutral', score: 0 },
        confidence: 0.95,
        ticketId: ticketData.id,
        ticketData: ticketData,
        isTyping: true,
      };
      
      setMessages(prev => [...prev, ticketMsg]);
      
      // Trigger ticket creation callback
      if (onTicketCreated) {
        onTicketCreated(ticketData);
      }

      // Persist ticket to backend
      try {
        await createTicket(ticketData);
      } catch (error) {
        console.error("Failed to persist ticket:", error);
      }
      
      // Simulate typing effect
      await new Promise(resolve => setTimeout(resolve, Math.min(ticketMsg.content.length * 20, 2000)));
      
      setMessages(prev => prev.map(msg => 
        msg.id === ticketMsg.id ? { ...msg, isTyping: false } : msg
      ));
      
      setIsTyping(false);
      
      // Update context - ticket created, ready for escalation
      setConversationContext(prev => ({
        ...prev,
        waitingForTicketDetails: false,
        ticketCreated: true,
        lastTicketId: ticketData.id,
      }));
      
      return;
    }

    // Check for escalation after ticket creation (only if ticket was created)
    if (conversationContext.ticketCreated) {
      const lowerMessage = userMessage.toLowerCase();
      const escalationKeywords = ['urgent', 'now', 'asap', 'immediately', 'need help now', 'emergency', 'i need help now! this is urgent!'];
      const isEscalation = escalationKeywords.some(keyword => lowerMessage.includes(keyword.toLowerCase()));
      
      if (isEscalation) {
        setIsTyping(true);
        
        // Show analyzing
        const analyzingMsg = {
          id: Date.now() + 0.1,
          type: 'ai',
          content: '🔍 Analyzing escalation request...',
          timestamp: new Date(),
          isAnalyzing: true,
        };
        setMessages(prev => [...prev, analyzingMsg]);
        
        await new Promise(resolve => setTimeout(resolve, 800));
        setMessages(prev => prev.filter(msg => !msg.isAnalyzing));
        
        // Show AI message about connecting to human agent
        const aiEscalationMsg = {
          id: Date.now() + 0.2,
          type: 'ai',
          content: 'I understand this is urgent. Let me connect you with a live human agent immediately.',
          timestamp: new Date(),
          isTyping: true,
        };
        setMessages(prev => [...prev, aiEscalationMsg]);
        
        await new Promise(resolve => setTimeout(resolve, 1000));
        setMessages(prev => prev.map(msg => 
          msg.id === aiEscalationMsg.id ? { ...msg, isTyping: false } : msg
        ));
        
        // Show finding agent animation
        setEscalationStatus({
          message: '🔍 Finding available agent...',
          status: 'searching',
        });
        
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        setEscalationStatus({
          message: '📞 Connecting to live agent...',
          status: 'connecting',
        });
        
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        setEscalationStatus({
          message: 'Agent will message you when online',
          status: 'pending',
        });
        
        // After 3 seconds, show Sarah (Tier 2) message
        setTimeout(() => {
          const agentMsg = {
            id: Date.now() + 2,
            type: 'agent',
            content: `Hi! I'm Sarah from Tier 2 Support. I can see you have ticket ${conversationContext.lastTicketId || 'INC-XXXX'} and need urgent assistance. I'm here to help you right away. Can you tell me more about what's happening?`,
            timestamp: new Date(),
            agentName: 'Sarah',
            agentTier: 'Tier 2',
          };
          
          setIsTyping(false);
          setMessages(prev => [...prev, agentMsg]);
          setEscalationStatus({
            message: 'Live agent active - Sarah (Tier 2)',
            status: 'active',
          });
          setIsAgentActive(true);
        }, 3000);
        
        return;
      }
    }

    // Generate AI response
    setIsTyping(true);
    
    // Show analyzing message
    const analyzingMsg = {
      id: Date.now() + 0.1,
      type: 'ai',
      content: '🔍 Analyzing request...',
      timestamp: new Date(),
      isAnalyzing: true,
    };
    setMessages(prev => [...prev, analyzingMsg]);
    
    await new Promise(resolve => setTimeout(resolve, 800));
    
    // Remove analyzing message
    setMessages(prev => prev.filter(msg => !msg.isAnalyzing));
    
    await new Promise(resolve => setTimeout(resolve, simulateTypingDelay(userMessage.length)));

    await new Promise(resolve => setTimeout(resolve, simulateTypingDelay(userMessage.length)));

    let aiResponse;
    try {
      const sessionId = conversationContext.sessionId || `session-${Date.now()}`;
      const backendRole = user ? mapRoleToBackend(user.role) : 'user';
      
      // Send conversation history (last 10 messages excluding the current user message)
      const conversationHistory = updatedHistory.slice(-11, -1); // Exclude current message
      
      const data = await sendMessageToBackend(
        userMessage, 
        sessionId, 
        backendRole, 
        conversationHistory
      );
      
      // Map backend response to frontend format
      aiResponse = {
        message: data.response,
        type: data.action,
        sentiment: { sentiment: data.sentiment || 'neutral', score: data.confidence_score || 0 },
        confidence: data.confidence_score || 0.9,
        source: data.sources && data.sources.length > 0
          ? [...new Set(data.sources.map(s => s.metadata.title))].join('\n')
          : null,
        sourceName: data.sources && data.sources.length > 0 ? data.sources[0].metadata.source : null,
        guardrail: (data.response.includes("violates system security policies") || data.response.includes("bypassing security controls")) ? { violated: true, category: 'security_policy' } : null,
        context: {
          ...conversationContext,
          sessionId: data.session_id,
        },
        // Preserve tier/severity info if needed for UI
        tier: data.tier,
        severity: data.severity
      };
      
      // Force type to guardrail if violation detected and not escalation
      if (aiResponse.guardrail && aiResponse.type !== 'escalation') {
        aiResponse.type = 'guardrail';
      }
      console.log(aiResponse);
    } catch (error) {
      aiResponse = {
        message: "I'm sorry, I'm having trouble connecting to the server. Please try again later.",
        type: 'error',
        sentiment: { sentiment: 'neutral', score: 0 },
        confidence: 0,
      };
    }
    
    // Handle escalation
    if (aiResponse.type === 'escalation') {
      setEscalationStatus({
        message: 'Connecting to live agent...',
        status: 'escalating',
      });
      
      // Simulate escalation progression
      setTimeout(async () => {
        setEscalationStatus({
          message: 'Agent connected: Sarah from Tier 1 Support',
          status: 'connected',
        });
        
        // Create escalation ticket automatically
        const escalationTicket = await generateTicketData([...messages, userMsg], userMessage);
        escalationTicket.priority = 'High';
        escalationTicket.escalated = true;
        escalationTicket.escalationReason = 'High sentiment detected';
        
        setTimeout(async () => {
          if (onTicketCreated) {
            onTicketCreated(escalationTicket);
          }
          
          // Persist escalation ticket to backend
          try {
            await createTicket(escalationTicket);
          } catch (error) {
            console.error("Failed to persist escalation ticket:", error);
          }
          
          // Add agent message (Sarah - Tier 2)
          const agentMsg = {
            id: Date.now() + 2,
            type: 'agent',
            content: `Hi! I'm Sarah from Tier 2 Support. I can see you're experiencing ${userMessage.toLowerCase().includes('urgent') ? 'an urgent issue' : 'some frustration'}. I've created ticket ${escalationTicket.id} and I'm here to help you right away. Can you tell me more about what's happening?`,
            timestamp: new Date(),
            agentName: 'Sarah',
            agentTier: 'Tier 2',
          };
          
          setIsTyping(false);
          setMessages(prev => [...prev, agentMsg]);
          setEscalationStatus({
            message: `Live agent active - Ticket ${escalationTicket.id} created`,
            status: 'active',
          });
        }, 2000);
      }, 1500);
      

      
      // Continue to display the AI response (acknowledgement or guardrail warning)
    }

    // Handle ticket details request
    if (aiResponse.type === 'ticket_details_request') {
      setConversationContext(prev => ({
        ...prev,
        waitingForTicketDetails: true,
        activeScriptId: aiResponse.context?.activeScriptId,
        currentStepIndex: aiResponse.context?.currentStepIndex,
        unresolvedAttempts: aiResponse.context?.unresolvedAttempts || 0,
      }));
    }

    // Update conversation context (script-based)
    if (aiResponse.context) {
      setConversationContext(prev => {
        return {
          ...prev,
          activeScriptId: aiResponse.context.activeScriptId !== undefined 
            ? aiResponse.context.activeScriptId 
            : prev.activeScriptId,
          currentStepIndex: aiResponse.context.currentStepIndex !== undefined
            ? aiResponse.context.currentStepIndex
            : prev.currentStepIndex,
          unresolvedAttempts: aiResponse.context.unresolvedAttempts !== undefined
            ? aiResponse.context.unresolvedAttempts
            : prev.unresolvedAttempts || 0,
          lastTicketId: aiResponse.context.lastTicketId || prev.lastTicketId,
        };
      });
    } else if (aiResponse.type === 'answer' && !aiResponse.options) {
      // No context provided - clear script state if response type indicates end
      setConversationContext(prev => ({
        ...prev,
        activeScriptId: null,
        currentStepIndex: null,
        unresolvedAttempts: prev.unresolvedAttempts || 0,
      }));
    }

    // Add AI message with typing effect
    const aiMsg = {
      id: Date.now() + 1,
      type: 'ai',
      content: aiResponse.message,
      timestamp: new Date(),
      sentiment: aiResponse.sentiment,
      confidence: aiResponse.confidence,
      source: aiResponse.source,
      sourceName: aiResponse.sourceName,
      messageType: aiResponse.type,
      options: aiResponse.options,
      guardrail: aiResponse.guardrail,

      tier: aiResponse.tier,
      severity: aiResponse.severity,
      isTyping: true,
    };

    console.log("aiMsg", aiMsg);

    setIsTyping(false);
    setMessages(prev => [...prev, aiMsg]);
    
    // Simulate typing effect for AI response
    await new Promise(resolve => setTimeout(resolve, Math.min(aiResponse.message.length * 20, 2000)));
    
    // Mark typing as complete
    setMessages(prev => prev.map(msg => 
      msg.id === aiMsg.id ? { ...msg, isTyping: false } : msg
    ));
  }, [messages, conversationContext, onTicketCreated]);

  // Handle initial message and auto-expand when message is provided
  useEffect(() => {
    if (isOpen && initialMessage && initialMessage !== lastInitialMessageRef.current) {
      // Reset the sent flag for new initial message
      initialMessageSentRef.current = false;
      lastInitialMessageRef.current = initialMessage;
      
      // If chat is collapsed, expand it first
      if (collapsed) {
        setCollapsed(false);
      }
    } else if (!initialMessage) {
      // Clear refs when initial message is cleared
      initialMessageSentRef.current = false;
      lastInitialMessageRef.current = null;
    }
  }, [initialMessage, isOpen, collapsed]);

  // Send initial message after chat is expanded and welcome message is shown
  useEffect(() => {
    if (isOpen && !collapsed && initialMessage && !initialMessageSentRef.current) {
      // Wait for welcome message to be set if needed
      if (messages.length === 0) {
        // Welcome message will be set by the other useEffect, wait for it
        return;
      }
      
      // Welcome message exists, send the initial message
      const timer = setTimeout(() => {
        if (!initialMessageSentRef.current) {
          initialMessageSentRef.current = true;
          handleSendMessage(initialMessage);
        }
      }, 800);
      
      return () => clearTimeout(timer);
    }
  }, [isOpen, collapsed, initialMessage, messages.length, handleSendMessage]);

  const handleClose = () => {
    // Reset chat state and collapse (but don't close completely)
    setMessages([]);
    setConversationContext({});
    setEscalationStatus(null);
    setIsAgentActive(false);
    setIsTyping(false);
    setCollapsed(true);
    initialMessageSentRef.current = false;
    lastInitialMessageRef.current = null;
    // Clear initial message in parent but keep chat open (so floating button shows)
    if (onClose) {
      // Only clear the initial message, don't close the chat
      onClose();
    }
  };

  const handleToggleCollapse = () => {
    const newCollapsedState = !collapsed;
    
    // Reset any stuck states when toggling
    setIsTyping(false);
    if (newCollapsedState) {
      // When collapsing, clear escalation status
      setEscalationStatus(null);
    }
    
    setCollapsed(newCollapsedState);
  };

  const handleOptionClick = (option) => {
    handleSendMessage(option);
  };

  if (!isOpen) return null;

  // When collapsed, show a floating button to reopen
  if (collapsed) {
    return (
      <Box
        sx={{
          position: 'fixed',
          bottom: 24,
          right: 24,
          zIndex: 1000,
        }}
      >
        <IconButton
          onClick={handleToggleCollapse}
          sx={{
            width: 'auto',
            height: 56,
            minWidth: 180,
            px: 2,
            backgroundColor: '#D4AF37',
            color: '#1a1a1a',
            borderRadius: '8px',
            boxShadow: '0 4px 12px rgba(212, 175, 55, 0.4)',
            '&:hover': {
              backgroundColor: '#E8C547',
              boxShadow: '0 6px 16px rgba(212, 175, 55, 0.5)',
              transform: 'scale(1.05)',
            },
            transition: 'all 0.3s ease',
          }}
        >
          <ChatIcon sx={{ fontSize: '24px', mr: 1 }} />
          <Typography sx={{ fontWeight: 'bold', fontSize: '16px', textTransform: 'none' }}>
            Chat with ACE
          </Typography>
        </IconButton>
      </Box>
    );
  }

  return (
    <ChatPanel elevation={8}>
      <ChatHeader>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
          <Box
            sx={{
              width: 40,
              height: 40,
              borderRadius: '12px',
              background: `linear-gradient(135deg, ${alpha('#D4AF37', 0.3)} 0%, ${alpha('#0052CC', 0.2)} 100%)`,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              border: `2px solid ${alpha('#D4AF37', 0.4)}`,
              boxShadow: `0 4px 12px ${alpha('#D4AF37', 0.2)}`,
            }}
          >
            <SmartToyIcon sx={{ color: '#D4AF37', fontSize: '24px' }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ color: '#D4AF37', fontWeight: 'bold', fontSize: '18px', lineHeight: 1.2 }}>
              ACE - AI Assistant
            </Typography>
            <Typography variant="caption" sx={{ color: alpha('#E0E0E0', 0.7), fontSize: '11px' }}>
              Always here to help
            </Typography>
          </Box>
        </Box>
        <IconButton
          onClick={handleClose}
          sx={{
            color: '#999999',
            '&:hover': {
              backgroundColor: alpha('#D4AF37', 0.1),
              color: '#D4AF37',
            },
            transition: 'all 0.2s ease',
          }}
        >
          <CloseIcon />
        </IconButton>
      </ChatHeader>

      <Box sx={{ display: 'flex', flexDirection: 'column', flex: 1, overflow: 'hidden' }}>
        <MessagesContainer ref={messagesContainerRef}>
          {messages.map((msg) => {
            // Skip analyzing messages (they're shown temporarily), but show processing messages
            if (msg.isAnalyzing) return null;
            
            return (
              <ChatMessage
                key={msg.id}
                message={msg.content}
                isUser={msg.type === 'user'}
                source={msg.source}
                confidence={msg.confidence}
                sentiment={msg.sentiment}
                type={msg.messageType === 'disambiguation' ? { options: msg.options, onOptionClick: handleOptionClick } : msg.messageType === 'guardrail' ? 'guardrail' : null}
                agentName={msg.agentName}
                agentTier={msg.agentTier}
                isTyping={msg.isTyping}
                guardrail={msg.guardrail}
                tier={msg.tier}
                severity={msg.severity}
              />
            );
          })}

          {isTyping && !escalationStatus && (
            <TypingIndicator>
              <Box
                sx={{
                  width: 24,
                  height: 24,
                  borderRadius: '50%',
                  background: `linear-gradient(135deg, ${alpha('#D4AF37', 0.3)} 0%, ${alpha('#0052CC', 0.2)} 100%)`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: `1px solid ${alpha('#D4AF37', 0.4)}`,
                }}
              >
                <SmartToyIcon sx={{ fontSize: '14px', color: '#D4AF37' }} />
              </Box>
              <Typography variant="caption" sx={{ color: '#D4AF37', fontWeight: 'medium' }}>
                {typingMessage}
              </Typography>
            </TypingIndicator>
          )}

          <Box ref={messagesEndRef} />

          {/* Escalation Banner */}
          <Collapse in={escalationStatus !== null}>
            <Alert
              severity="warning"
              sx={{
                mt: 2,
                backgroundColor: alpha('#FF9500', 0.2),
                color: '#FF9500',
                border: `1px solid ${alpha('#FF9500', 0.4)}`,
                borderRadius: '12px',
                '& .MuiAlert-icon': {
                  color: '#FF9500',
                },
                boxShadow: `0 4px 12px ${alpha('#FF9500', 0.2)}`,
              }}
            >
              {escalationStatus?.message || 'Connecting to live agent...'}
            </Alert>
          </Collapse>
        </MessagesContainer>

        <Box
          sx={{
            borderTop: `2px solid ${alpha('#D4AF37', 0.2)}`,
            padding: '16px 20px',
            background: `linear-gradient(180deg, ${alpha('#121212', 1)} 0%, ${alpha('#1a1a1a', 1)} 100%)`,
            position: 'relative',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: 0,
              right: 0,
              height: '2px',
              background: `linear-gradient(90deg, transparent, ${alpha('#D4AF37', 0.6)}, transparent)`,
            },
          }}
        >
          <ChatInput
            onSend={handleSendMessage}
            disabled={isTyping || escalationStatus?.status === 'escalating'}
          />
          {/* Collapse Button */}
          <Box sx={{ display: 'flex', justifyContent: 'center', mt: 1 }}>
            <IconButton
              onClick={handleToggleCollapse}
              sx={{
                color: '#D4AF37',
                backgroundColor: alpha('#D4AF37', 0.1),
                borderRadius: '8px',
                width: '100%',
                py: 0.5,
                '&:hover': {
                  backgroundColor: alpha('#D4AF37', 0.2),
                  color: '#E8C547',
                },
                transition: 'all 0.2s ease',
              }}
            >
              <ExpandMoreIcon sx={{ fontSize: '24px' }} />
            </IconButton>
          </Box>
        </Box>
      </Box>
    </ChatPanel>
  );
};

export default AIChatPanel;

