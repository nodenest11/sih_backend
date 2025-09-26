"""
LSTM/GRU Autoencoder for sequence-based anomaly detection
"""
import torch
import torch.nn as nn
import numpy as np
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any
from torch.utils.data import DataLoader, TensorDataset
from sklearn.preprocessing import MinMaxScaler
from ..config.ai_config import CONFIG
from ..schemas.ai_schemas import ProcessedFeatures, ModelPrediction
from ..preprocessors.data_preprocessor import DataPreprocessor

class LSTMAutoencoder(nn.Module):
    """
    LSTM Autoencoder for temporal anomaly detection
    Learns normal sequences of tourist movement patterns
    """
    
    def __init__(self, 
                 input_size: int,
                 hidden_size: int, 
                 num_layers: int,
                 dropout: float = 0.2):
        super(LSTMAutoencoder, self).__init__()
        
        self.input_size = input_size
        self.hidden_size = hidden_size
        self.num_layers = num_layers
        
        # Encoder
        self.encoder_lstm = nn.LSTM(
            input_size, 
            hidden_size, 
            num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
        # Decoder
        self.decoder_lstm = nn.LSTM(
            hidden_size,
            input_size,
            num_layers, 
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0
        )
        
    def forward(self, x):
        batch_size, seq_len, _ = x.shape
        
        # Encoder
        encoded, (hidden, cell) = self.encoder_lstm(x)
        
        # Use the last hidden state as the context vector
        context = hidden[-1].unsqueeze(1).repeat(1, seq_len, 1)
        
        # Decoder - reconstruct the input sequence
        decoded, _ = self.decoder_lstm(context)
        
        return decoded

class LSTMAutoencoderDetector:
    """
    LSTM Autoencoder detector for temporal anomaly detection
    """
    
    def __init__(self):
        self.config = CONFIG.lstm
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        self.scaler = MinMaxScaler()
        self.preprocessor = DataPreprocessor()
        self.is_trained = False
        self.reconstruction_threshold = 0.1  # Will be set during training
        
    def _prepare_sequences(self, features_list: List[ProcessedFeatures]) -> np.ndarray:
        """
        Prepare sequential data for LSTM training/prediction
        
        Returns:
            Array of shape (num_sequences, sequence_length, num_features)
        """
        if not features_list:
            return np.array([]).reshape(0, self.config.sequence_length, self.config.input_features)
        
        # Group by tourist_id and sort by timestamp
        tourist_groups = self.preprocessor.group_by_tourist(features_list)
        
        all_sequences = []
        
        for tourist_id, tourist_features in tourist_groups.items():
            # Prepare feature matrix for this tourist
            feature_matrix = self.preprocessor.prepare_isolation_forest_data(tourist_features)
            
            if len(feature_matrix) < self.config.sequence_length:
                continue  # Skip if not enough data points
                
            # Create sliding windows
            sequences = self.preprocessor.create_sliding_windows(
                feature_matrix, 
                self.config.sequence_length,
                step_size=1
            )
            
            all_sequences.extend(sequences)
            
        return np.array(all_sequences)
    
    def train(self, training_features: List[ProcessedFeatures]) -> Dict[str, Any]:
        """
        Train the LSTM autoencoder
        
        Args:
            training_features: List of processed features for training
            
        Returns:
            Training metrics and information
        """
        if not training_features:
            raise ValueError("Training features cannot be empty")
        
        # Prepare sequential data
        sequences = self._prepare_sequences(training_features)
        
        if sequences.shape[0] < 10:
            raise ValueError("Need at least 10 sequences for training")
            
        # Normalize features
        original_shape = sequences.shape
        sequences_reshaped = sequences.reshape(-1, sequences.shape[-1])
        sequences_normalized = self.scaler.fit_transform(sequences_reshaped)
        sequences = sequences_normalized.reshape(original_shape)
        
        # Convert to PyTorch tensors
        X_tensor = torch.FloatTensor(sequences).to(self.device)
        
        # Create model
        self.model = LSTMAutoencoder(
            input_size=self.config.input_features,
            hidden_size=self.config.hidden_size,
            num_layers=self.config.num_layers,
            dropout=self.config.dropout
        ).to(self.device)
        
        # Setup training
        criterion = nn.MSELoss()
        optimizer = torch.optim.Adam(self.model.parameters(), lr=self.config.learning_rate)
        
        # Create data loader
        dataset = TensorDataset(X_tensor, X_tensor)  # Input and target are the same for autoencoder
        dataloader = DataLoader(dataset, batch_size=self.config.batch_size, shuffle=True)
        
        # Training loop
        train_losses = []
        self.model.train()
        
        for epoch in range(self.config.epochs):
            epoch_loss = 0.0
            
            for batch_X, batch_y in dataloader:
                optimizer.zero_grad()
                
                # Forward pass
                reconstructed = self.model(batch_X)
                loss = criterion(reconstructed, batch_y)
                
                # Backward pass
                loss.backward()
                optimizer.step()
                
                epoch_loss += loss.item()
                
            avg_loss = epoch_loss / len(dataloader)
            train_losses.append(avg_loss)
            
            if (epoch + 1) % 10 == 0:
                print(f"Epoch [{epoch+1}/{self.config.epochs}], Loss: {avg_loss:.6f}")
        
        # Set reconstruction threshold based on training data
        self.model.eval()
        with torch.no_grad():
            all_reconstructions = self.model(X_tensor)
            reconstruction_errors = torch.mean((X_tensor - all_reconstructions) ** 2, dim=(1, 2))
            self.reconstruction_threshold = float(torch.quantile(reconstruction_errors, 0.95))
        
        self.is_trained = True
        
        training_info = {
            'model_name': 'lstm_autoencoder',
            'training_sequences': sequences.shape[0],
            'sequence_length': self.config.sequence_length,
            'feature_count': self.config.input_features,
            'final_loss': train_losses[-1] if train_losses else 0.0,
            'reconstruction_threshold': self.reconstruction_threshold,
            'device': str(self.device),
            'training_timestamp': datetime.now()
        }
        
        return training_info
    
    def predict(self, features_sequence: List[ProcessedFeatures]) -> ModelPrediction:
        """
        Predict temporal anomaly score for a sequence of features
        
        Args:
            features_sequence: List of ProcessedFeatures in temporal order
            
        Returns:
            ModelPrediction with temporal anomaly analysis
        """
        if not self.is_trained or not self.model:
            return ModelPrediction(
                model_name="lstm_autoencoder",
                score=0.5,
                confidence=0.0,
                details={
                    'trained': False,
                    'message': 'Model not trained yet',
                    'reconstruction_error': 0.0,
                    'is_anomaly': False
                },
                timestamp=datetime.now()
            )
        
        if len(features_sequence) < self.config.sequence_length:
            # Not enough data for prediction
            return ModelPrediction(
                model_name="lstm_autoencoder",
                score=0.5,
                confidence=0.0,
                details={
                    'trained': True,
                    'message': 'Insufficient sequence length for prediction',
                    'required_length': self.config.sequence_length,
                    'provided_length': len(features_sequence),
                    'reconstruction_error': 0.0,
                    'is_anomaly': False
                },
                timestamp=datetime.now()
            )
        
        # Take the most recent sequence_length features
        recent_features = features_sequence[-self.config.sequence_length:]
        
        # Prepare feature matrix
        feature_matrix = self.preprocessor.prepare_isolation_forest_data(recent_features)
        
        # Normalize
        feature_matrix = self.scaler.transform(feature_matrix)
        
        # Convert to tensor
        sequence_tensor = torch.FloatTensor(feature_matrix).unsqueeze(0).to(self.device)
        
        # Predict
        self.model.eval()
        with torch.no_grad():
            reconstructed = self.model(sequence_tensor)
            
            # Calculate reconstruction error
            reconstruction_error = torch.mean((sequence_tensor - reconstructed) ** 2).item()
            
            # Determine if it's an anomaly
            is_anomaly = reconstruction_error > self.reconstruction_threshold
            
            # Normalize score (lower reconstruction error = higher safety score)
            max_error = self.reconstruction_threshold * 2  # Reasonable upper bound
            normalized_score = 1.0 - min(reconstruction_error / max_error, 1.0)
            
            # Confidence based on how far from threshold
            confidence = min(abs(reconstruction_error - self.reconstruction_threshold) / self.reconstruction_threshold, 1.0)
        
        details = {
            'trained': True,
            'reconstruction_error': float(reconstruction_error),
            'reconstruction_threshold': self.reconstruction_threshold,
            'is_anomaly': is_anomaly,
            'sequence_length': len(recent_features),
            'interpretation': self._interpret_temporal_anomaly(reconstruction_error, is_anomaly)
        }
        
        return ModelPrediction(
            model_name="lstm_autoencoder",
            score=normalized_score,
            confidence=confidence,
            details=details,
            timestamp=datetime.now()
        )
    
    def _interpret_temporal_anomaly(self, reconstruction_error: float, is_anomaly: bool) -> str:
        """Provide interpretation of temporal anomaly detection result"""
        if not is_anomaly:
            return "Movement sequence appears normal"
        
        if reconstruction_error > self.reconstruction_threshold * 2:
            return "Highly unusual movement sequence detected"
        elif reconstruction_error > self.reconstruction_threshold * 1.5:
            return "Moderately unusual movement sequence detected"
        else:
            return "Slightly unusual movement sequence detected"
    
    def save_model(self, filepath: Optional[str] = None) -> str:
        """Save the trained model to disk"""
        if not self.is_trained or not self.model:
            raise ValueError("Model must be trained before saving")
            
        if filepath is None:
            filepath = os.path.join(CONFIG.model_save_dir, "lstm_autoencoder_model.pth")
            
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        model_data = {
            'model_state_dict': self.model.state_dict(),
            'scaler': self.scaler,
            'config': self.config.__dict__,
            'reconstruction_threshold': self.reconstruction_threshold,
            'is_trained': self.is_trained,
            'save_timestamp': datetime.now()
        }
        
        torch.save(model_data, filepath)
        return filepath
    
    def load_model(self, filepath: Optional[str] = None) -> bool:
        """Load a trained model from disk"""
        if filepath is None:
            filepath = os.path.join(CONFIG.model_save_dir, "lstm_autoencoder_model.pth")
            
        if not os.path.exists(filepath):
            return False
            
        try:
            model_data = torch.load(filepath, map_location=self.device)
            
            # Recreate model
            self.model = LSTMAutoencoder(
                input_size=self.config.input_features,
                hidden_size=self.config.hidden_size,
                num_layers=self.config.num_layers,
                dropout=self.config.dropout
            ).to(self.device)
            
            # Load state
            self.model.load_state_dict(model_data['model_state_dict'])
            self.scaler = model_data['scaler']
            self.reconstruction_threshold = model_data.get('reconstruction_threshold', 0.1)
            self.is_trained = model_data.get('is_trained', False)
            
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            'model_name': 'lstm_autoencoder',
            'is_trained': self.is_trained,
            'sequence_length': self.config.sequence_length,
            'hidden_size': self.config.hidden_size,
            'num_layers': self.config.num_layers,
            'reconstruction_threshold': self.reconstruction_threshold if self.is_trained else None,
            'device': str(self.device)
        }