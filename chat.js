const express = require('express');
const { body, validationResult } = require('express-validator');
const Chat = require('../models/Chat');
const { auth } = require('../middleware/auth');

const router = express.Router();

// Simple AI response generator (replace with actual AI service)
const generateAIResponse = async (message, userLanguage = 'en') => {
  // This is a simple mock AI response
  // In a real application, you would integrate with OpenAI, Claude, or another AI service
  
  const responses = {
    en: {
      greeting: "Hello! I'm Jarvis, your AI assistant. How can I help you today?",
      help: "I can help you with various tasks like answering questions, writing code, analyzing data, and more. What would you like to know?",
      weather: "I can help you check the weather! Please provide your location.",
      code: "I'd be happy to help you with coding! What programming language are you working with?",
      default: "That's an interesting question! Let me think about that for a moment..."
    },
    hi: {
      greeting: "नमस्ते! मैं जारविस हूं, आपका AI सहायक। मैं आज आपकी कैसे मदद कर सकता हूं?",
      help: "मैं आपकी विभिन्न कार्यों में मदद कर सकता हूं जैसे प्रश्नों का उत्तर देना, कोड लिखना, डेटा विश्लेषण और बहुत कुछ। आप क्या जानना चाहते हैं?",
      weather: "मैं आपको मौसम की जानकारी देने में मदद कर सकता हूं! कृपया अपना स्थान बताएं।",
      code: "मैं आपकी कोडिंग में मदद करने में खुशी महसूस करूंगा! आप किस प्रोग्रामिंग भाषा के साथ काम कर रहे हैं?",
      default: "यह एक दिलचस्प सवाल है! मुझे इसके बारे में सोचने के लिए एक पल दें..."
    }
  };

  const langResponses = responses[userLanguage] || responses.en;
  
  // Simple keyword matching
  const lowerMessage = message.toLowerCase();
  
  if (lowerMessage.includes('hello') || lowerMessage.includes('hi') || lowerMessage.includes('नमस्ते')) {
    return langResponses.greeting;
  } else if (lowerMessage.includes('help') || lowerMessage.includes('मदद')) {
    return langResponses.help;
  } else if (lowerMessage.includes('weather') || lowerMessage.includes('मौसम')) {
    return langResponses.weather;
  } else if (lowerMessage.includes('code') || lowerMessage.includes('programming') || lowerMessage.includes('कोड')) {
    return langResponses.code;
  } else {
    return langResponses.default;
  }
};

// @route   POST /api/chat/send
// @desc    Send a message to Jarvis AI
// @access  Private
router.post('/send', [
  auth,
  body('message')
    .trim()
    .isLength({ min: 1, max: 1000 })
    .withMessage('Message must be between 1 and 1000 characters')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { message, chatId } = req.body;
    const userId = req.user._id;

    let chat;
    
    // If chatId is provided, find existing chat, otherwise create new one
    if (chatId) {
      chat = await Chat.findOne({ _id: chatId, userId });
      if (!chat) {
        return res.status(404).json({
          error: 'Chat not found'
        });
      }
    } else {
      // Create new chat
      chat = new Chat({
        userId,
        language: req.user.language,
        title: message.substring(0, 50) + (message.length > 50 ? '...' : '')
      });
    }

    // Add user message
    chat.addMessage(message, 'user');

    // Generate AI response
    const aiResponse = await generateAIResponse(message, req.user.language);
    
    // Add AI response
    chat.addMessage(aiResponse, 'ai');

    await chat.save();

    res.json({
      message: 'Message sent successfully',
      chat: {
        id: chat._id,
        title: chat.title,
        messages: chat.getRecentMessages(),
        analytics: chat.analytics
      }
    });

  } catch (error) {
    console.error('Send message error:', error);
    res.status(500).json({
      error: 'Server error while sending message'
    });
  }
});

// @route   GET /api/chat/conversations
// @desc    Get user's chat conversations
// @access  Private
router.get('/conversations', auth, async (req, res) => {
  try {
    const { page = 1, limit = 10 } = req.query;
    const skip = (page - 1) * limit;

    const chats = await Chat.find({ userId: req.user._id })
      .select('title lastActivity analytics.messageCount createdAt')
      .sort({ lastActivity: -1 })
      .skip(skip)
      .limit(parseInt(limit));

    const total = await Chat.countDocuments({ userId: req.user._id });

    res.json({
      chats,
      pagination: {
        current: parseInt(page),
        total: Math.ceil(total / limit),
        hasNext: skip + chats.length < total,
        hasPrev: page > 1
      }
    });

  } catch (error) {
    console.error('Get conversations error:', error);
    res.status(500).json({
      error: 'Server error while fetching conversations'
    });
  }
});

// @route   GET /api/chat/:chatId
// @desc    Get specific chat with messages
// @access  Private
router.get('/:chatId', auth, async (req, res) => {
  try {
    const { chatId } = req.params;
    const { limit = 50 } = req.query;

    const chat = await Chat.findOne({ _id: chatId, userId: req.user._id });
    
    if (!chat) {
      return res.status(404).json({
        error: 'Chat not found'
      });
    }

    res.json({
      chat: {
        id: chat._id,
        title: chat.title,
        messages: chat.getRecentMessages(parseInt(limit)),
        analytics: chat.analytics,
        settings: chat.settings,
        language: chat.language
      }
    });

  } catch (error) {
    console.error('Get chat error:', error);
    res.status(500).json({
      error: 'Server error while fetching chat'
    });
  }
});

// @route   PUT /api/chat/:chatId/title
// @desc    Update chat title
// @access  Private
router.put('/:chatId/title', [
  auth,
  body('title')
    .trim()
    .isLength({ min: 1, max: 100 })
    .withMessage('Title must be between 1 and 100 characters')
], async (req, res) => {
  try {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      return res.status(400).json({
        error: 'Validation failed',
        details: errors.array()
      });
    }

    const { chatId } = req.params;
    const { title } = req.body;

    const chat = await Chat.findOneAndUpdate(
      { _id: chatId, userId: req.user._id },
      { title },
      { new: true }
    );

    if (!chat) {
      return res.status(404).json({
        error: 'Chat not found'
      });
    }

    res.json({
      message: 'Chat title updated successfully',
      title: chat.title
    });

  } catch (error) {
    console.error('Update chat title error:', error);
    res.status(500).json({
      error: 'Server error while updating chat title'
    });
  }
});

// @route   DELETE /api/chat/:chatId
// @desc    Delete a chat conversation
// @access  Private
router.delete('/:chatId', auth, async (req, res) => {
  try {
    const { chatId } = req.params;

    const chat = await Chat.findOneAndDelete({ _id: chatId, userId: req.user._id });

    if (!chat) {
      return res.status(404).json({
        error: 'Chat not found'
      });
    }

    res.json({
      message: 'Chat deleted successfully'
    });

  } catch (error) {
    console.error('Delete chat error:', error);
    res.status(500).json({
      error: 'Server error while deleting chat'
    });
  }
});

// @route   POST /api/chat/:chatId/clear
// @desc    Clear all messages in a chat
// @access  Private
router.post('/:chatId/clear', auth, async (req, res) => {
  try {
    const { chatId } = req.params;

    const chat = await Chat.findOne({ _id: chatId, userId: req.user._id });

    if (!chat) {
      return res.status(404).json({
        error: 'Chat not found'
      });
    }

    chat.clearChat();
    await chat.save();

    res.json({
      message: 'Chat cleared successfully'
    });

  } catch (error) {
    console.error('Clear chat error:', error);
    res.status(500).json({
      error: 'Server error while clearing chat'
    });
  }
});

module.exports = router; 