const mongoose = require('mongoose');

const messageSchema = new mongoose.Schema({
  content: {
    type: String,
    required: true,
    trim: true
  },
  sender: {
    type: String,
    enum: ['user', 'ai'],
    required: true
  },
  timestamp: {
    type: Date,
    default: Date.now
  },
  messageType: {
    type: String,
    enum: ['text', 'image', 'file', 'voice'],
    default: 'text'
  },
  metadata: {
    language: String,
    sentiment: String,
    confidence: Number,
    processingTime: Number
  }
});

const chatSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  title: {
    type: String,
    default: 'New Conversation'
  },
  messages: [messageSchema],
  language: {
    type: String,
    enum: ['en', 'hi', 'es', 'fr', 'de', 'ja', 'ko', 'zh'],
    default: 'en'
  },
  isActive: {
    type: Boolean,
    default: true
  },
  lastActivity: {
    type: Date,
    default: Date.now
  },
  settings: {
    aiPersonality: {
      type: String,
      enum: ['friendly', 'professional', 'creative', 'technical'],
      default: 'friendly'
    },
    responseLength: {
      type: String,
      enum: ['short', 'medium', 'long'],
      default: 'medium'
    },
    includeCode: {
      type: Boolean,
      default: true
    }
  },
  analytics: {
    totalMessages: {
      type: Number,
      default: 0
    },
    userMessages: {
      type: Number,
      default: 0
    },
    aiMessages: {
      type: Number,
      default: 0
    },
    averageResponseTime: {
      type: Number,
      default: 0
    }
  }
}, {
  timestamps: true
});

// Indexes for better query performance
chatSchema.index({ userId: 1, createdAt: -1 });
chatSchema.index({ userId: 1, lastActivity: -1 });

// Virtual for message count
chatSchema.virtual('messageCount').get(function() {
  return this.messages.length;
});

// Method to add message
chatSchema.methods.addMessage = function(content, sender, messageType = 'text', metadata = {}) {
  const message = {
    content,
    sender,
    messageType,
    timestamp: new Date(),
    metadata: {
      language: this.language,
      ...metadata
    }
  };
  
  this.messages.push(message);
  this.lastActivity = new Date();
  
  // Update analytics
  this.analytics.totalMessages += 1;
  if (sender === 'user') {
    this.analytics.userMessages += 1;
  } else {
    this.analytics.aiMessages += 1;
  }
  
  return message;
};

// Method to get recent messages
chatSchema.methods.getRecentMessages = function(limit = 50) {
  return this.messages.slice(-limit);
};

// Method to clear chat
chatSchema.methods.clearChat = function() {
  this.messages = [];
  this.analytics = {
    totalMessages: 0,
    userMessages: 0,
    aiMessages: 0,
    averageResponseTime: 0
  };
  this.lastActivity = new Date();
};

// Ensure virtual fields are serialized
chatSchema.set('toJSON', { virtuals: true });

module.exports = mongoose.model('Chat', chatSchema); 