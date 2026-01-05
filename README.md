# MLSA Cards DApp
Play. Learn. Collect. Mint.

A full-stack NFT collectible card game where users solve problems to earn points, purchase digital cards, and mint them as ERC-721 NFTs on the blockchain.
A full-stack Web3-powered gamified learning platform where users solve domain-based challenges, earn points, unlock collectible cards, and mint them as ERC-721 NFTs with verifiable on-chain ownership.

Developed as a collaborative MLSA  project, showcasing secure authentication, blockchain integration, and real-world full-stack architecture.

## 🎯 Project Vision

MLSA Cards aims to bridge learning and ownership by transforming skill acquisition into an engaging, collectible-driven experience.

- 1.Instead of passive learning, users:

- 2.actively solve problems

- 3.earn verifiable rewards

- 4.gain permanent digital ownership of achievements via NFTs.

## 📑 Table of Contents
- [Project Vision](#-project-vision)
- [What Can Users Do?](#-what-can-users-do)
- [Core Features](#-core-features)
- [UI & User Experience](#-ui--user-experience)
- [Tech Stack](#-tech-stack)
- [Prerequisites](#-prerequisites)
- [Setup Instructions](#-setup-instructions)
- [Why This Project Stands Out (MLSA Impact)](#-why-this-project-stands-out-mlsa-impact)

## 🎮 About
MLSA Cards is a gamified learning platform that combines education with blockchain technology. Users can:
- **Solve Problems**: Answer questions across multiple categories (Math, Science, Tech, Geography, etc.)
- **Earn Points**: Get rewarded with points for correct answers
- **Collect Cards**: Purchase unique skill cards from the store using earned points
- **Mint NFTs**: Convert owned cards into blockchain-backed NFTs with permanent ownership
- **Hybrid Authentication**: Login with Google OAuth for easy access or MetaMask for Web3 natives

## 🎮 What Can Users Do?
 🧠 Solve Problems
 - Answer curated questions across multiple categories (Programming, CS, Web Dev, AI/ML, Science, Geography, etc.)

 ⭐ Earn & Track Points
 - Real-time scoring, accuracy tracking, streaks, and level progression

 🃏 Collect Skill Cards
 - Spend earned points to purchase collectible cards with defined rarity

 🎨 Mint NFTs
 - Convert owned cards into ERC-721 NFTs backed by blockchain verification

 🔐 Hybrid Authentication
 - Login via Google OAuth or MetaMask with optional wallet linking

## ✨ Features

- **🔐Dual Authentication System**
  - Google OAuth integration for seamless onboarding
  - MetaMask wallet authentication for blockchain users
  - Optional wallet linking to enable NFT minting for OAuth users

- **💾Persistent Data Storage**
  - SQLite database for user profiles, cards, and progress
  - All data persists across sessions and browser clears

- **🧠Problem Solving System**
  - 50+ questions across 10+ categories
  - Real-time point tracking
  - Progress saved per user

- **🛒Card Store**
  - 10 unique collectible cards with different rarities
  - Dynamic pricing based on rarity
  - Purchase tracking and ownership management

- **🎨NFT Minting**
  - Server-side transaction signing (gasless for users)
  - IPFS metadata storage via Pinata
  - ERC-721 compliant smart contract
  - Transaction history and on-chain verification

  ## 🖥 UI & User Experience

- Designed using Figma and implemented with a cslean, responsive UI.
- Key interfaces include:
- Authentication (Login / Signup)
- User Dashboard (stats, points, cards, level)
- Quiz Interface (category-based questions)
- Card Marketplace
- NFT Collection with blockchain links

## 🛠 Tech Stack

**Frontend**
- Vanilla JavaScript (no framework)
- Ethers.js v6 for Web3 interactions
- Responsive CSS with modern design

**Backend**
- FastAPI (Python)
- SQLAlchemy ORM with SQLite
- Authlib for OAuth 2.0
- JWT authentication
- Web3.py for blockchain interactions

**Blockchain**
- Solidity smart contracts
- Hardhat development environment
- ERC-721 token standard
- Support for Ethereum Sepolia, Polygon Amoy/Mainnet

**Storage**
- SQLite for application data
- Pinata (IPFS) for NFT metadata

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** Python 3.10–3.11 required. Python 3.13 not supported.
- **MetaMask** browser extension
- **Google OAuth Credentials** (for OAuth login)
- **Pinata Account** (for IPFS storage)

## 🚀 Setup Instructions

### 1. Clone the Repository

```powershell
git clone <your-repo-url>
cd PW
```

### 2. Smart Contract Setup

```powershell
cd smart-contracts
npm install
```

Create `.env` from `.env.example`:
```powershell
cp .env.example .env
```

Fill in your `.env`:
```env
# For local development
ALCHEMY_SEPOLIA_RPC=https://eth-sepolia.g.alchemy.com/v2/your-key
PRIVATE_KEY=your-wallet-private-key
ETHERSCAN_API_KEY=your-etherscan-api-key
```

**Deploy the contract:**

For local development:
```powershell
# Terminal 1: Start Hardhat node
npx hardhat node

# Terminal 2: Deploy
npm run deploy:local
```

For testnet (Sepolia):
```powershell
npm run deploy:sepolia
```

**Save the deployed contract address** - you'll need it for the backend!

### 3. Backend Setup

```powershell
cd ../backend
python -m venv .venv
.\.venv\Scripts\Activate
pip install -r requirements.txt
```

Create `.env` from `.env.example`:
```powershell
cp .env.example .env
```

Configure your backend `.env`:
```env
# Blockchain connection
RPC_URL=http://127.0.0.1:8545
CHAIN_ID=31337
PRIVATE_KEY=0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80
CONTRACT_ADDRESS=<your-deployed-contract-address>

# IPFS Storage
PINATA_JWT=your-pinata-jwt-token

# Security
JWT_SECRET=your-strong-random-secret

# CORS
FRONTEND_ORIGIN=http://localhost:8000

# Google OAuth (get from https://console.cloud.google.com/apis/credentials)
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
```

**Setup Google OAuth:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/apis/credentials)
2. Create a new OAuth 2.0 Client ID
3. Add authorized redirect URI: `http://localhost:8000/auth/google/callback`
4. Copy Client ID and Client Secret to `.env`

**Create card images:**

Place card images in `backend/static/images/cards/`:
- aiml.png
- cloud.png
- web.png
- gd.png
- crpr.png
- broadcast.png
- cyber.png
- arvr.png
- app.png
- video.png

## 🎯 Running the Application

### Start Backend Server

```powershell
cd backend
.\.venv\Scripts\Activate
uvicorn app.main:app --reload --port 8000
```

### Access the Application

Open your browser and navigate to:
```
http://localhost:8000
```

## 🎮 How to Use

### 1. Create an Account

**Option A: Google OAuth**
- Click "Continue with Google"
- Sign in with your Google account
- Automatically creates your profile

**Option B: MetaMask**
- Click "Connect Wallet"
- Approve MetaMask connection
- Sign authentication message
- Account created with your wallet address

### 2. Earn Points

- Navigate to **Problems** page
- Click "Load a Problem"
- Answer questions correctly
- Earn 2-5 points per correct answer
- Track progress: Solved X / 50 problems

### 3. Purchase Cards

- Go to **Store** page
- Browse 10 unique cards (10-22 points each)
- Click "Buy Now" on desired cards
- Points deducted automatically
- Cards marked as "Owned" after purchase

### 4. View Collection

- Visit **My Cards** page
- See all purchased cards with details
- View rarity, description, and purchase date

### 5. Mint NFTs

**Requirements:**
- Must have wallet linked (MetaMask or linked OAuth account)
- Must own the card you want to mint

**Steps:**
- Go to **My Cards**
- Click "🎨 Mint as NFT" on any owned card
- Confirm transaction (server pays gas)
- NFT minted to your wallet address
- View transaction hash and token ID

## 🔧 Configuration

### Chain IDs
- Local Hardhat: `31337`
- Ethereum Sepolia: `11155111`
- Polygon Amoy: `80002`
- Polygon Mainnet: `137`

### Network RPC URLs
Update `RPC_URL` in backend `.env`:
- Local: `http://127.0.0.1:8545`
- Sepolia: `https://eth-sepolia.g.alchemy.com/v2/YOUR_KEY`
- Polygon Amoy: `https://polygon-amoy.g.alchemy.com/v2/YOUR_KEY`
- Polygon Mainnet: `https://polygon-mainnet.g.alchemy.com/v2/YOUR_KEY`

## 🧪 Testing

### Smart Contract Tests
```powershell
cd smart-contracts
npm test
```

### Backend Tests
```powershell
cd backend
.\.venv\Scripts\Activate
pytest
```

## 📝 Notes

- **Gas Payments**: Server pays gas for minting (via PRIVATE_KEY in backend .env)
- **Security**: Never commit `.env` files to git
- **Database**: SQLite file `mlsa_cards.db` created automatically on first run
- **Metadata**: All NFT metadata stored on IPFS via Pinata
- **Local Testing**: Use Hardhat's default test accounts for development

## 🔐 Security Considerations

- Store sensitive keys in `.env` files (never commit)
- Use separate wallets for development and production
- Rotate JWT secrets regularly
- Enable CORS only for trusted origins
- Validate all user inputs on backend

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Troubleshooting

**"Auth failed" errors:**
- Clear localStorage in browser DevTools
- Ensure JWT_SECRET is set in backend `.env`

**"Contract not found" errors:**
- Verify CONTRACT_ADDRESS in backend `.env`
- Ensure Hardhat node is running (for local)
- Check RPC_URL and CHAIN_ID match your network

**"Insufficient points" errors:**
- Solve more problems to earn points
- Check points balance on homepage

**Mint fails:**
- Ensure wallet is connected
- Verify PRIVATE_KEY has funds for gas
- Check RPC connection
- Confirm contract is deployed

**Google OAuth errors:**
- Verify redirect URI matches exactly: `http://localhost:8000/auth/google/callback`
- Check CLIENT_ID and CLIENT_SECRET are correct
- Ensure OAuth consent screen is configured

## 🌟 Why This Project Stands Out (MLSA Impact)

- Demonstrates real-world Web3 integration
- Implements secure hybrid authentication
- Uses production-style backend architecture
- Encourages learning through gamification
- Built via collaborative, contribution-based development