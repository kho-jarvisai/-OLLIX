import numpy as np
import pandas as pd
from scipy.optimize import minimize
from ta.momentum import RSIIndicator

class QuantitativeAnalyst:

    @staticmethod
    def generate_actionable_signals(prices_df: pd.DataFrame, weights: pd.Series) -> pd.DataFrame:
        """Combines denoised portfolio weights with price action to generate explicit predictions."""
        signals = pd.DataFrame(index=weights.index)
        signals['Denoised_Weight'] = weights
        
        predictions = []
        reasons = []
        
        for ticker in weights.index:
            # Pull individual price series for indicator cross-reference
            series = prices_df[ticker]
            sma_50 = series.rolling(50).mean().iloc[-1]
            sma_200 = series.rolling(200).mean().iloc[-1]
            current_price = series.iloc[-1]
            
            # Actionable Predictive Logic: High structural weight + Bullish technical breakout
            if weights[ticker] > weights.mean() and current_price > sma_50 and sma_50 > sma_200:
                predictions.append("STRONGBUY")
                reasons.append("High structural signal + Bullish Moving Average crossover.")
            elif current_price < sma_200:
                predictions.append("AVOID/SELL")
                reasons.append("Asset under severe macro pressure; trading below 200-day SMA.")
            else:
                predictions.append("HOLD")
                reasons.append("Stable allocation; normal structural boundary parameters.")
                
        signals['Prediction'] = predictions
        signals['Trade_Reasoning'] = reasons
        return signals

    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        processed = pd.DataFrame(index=df.index)
        processed['Close'] = df
        processed['SMA_50'] = df.rolling(window=50).mean()
        processed['SMA_200'] = df.rolling(window=200).mean()
        processed['RSI'] = RSIIndicator(close=df, window=14).rsi()
        return processed

    @staticmethod
    def clean_correlation_matrix(returns_df: pd.DataFrame) -> pd.DataFrame:
        T, N = returns_df.shape
        if T <= N:
            return returns_df.corr()
        corr = returns_df.corr().fillna(0).values
        eigenvalues, eigenvectors = np.linalg.eigh(corr)
        q = float(T) / N
        sigma_sq = 1.0 - np.max(eigenvalues) / N
        lambda_max = sigma_sq * (1 + (1/q)**0.5)**2
        noisy_indices = eigenvalues <= lambda_max
        if np.any(noisy_indices):
            avg_noisy_eigenvalue = np.mean(eigenvalues[noisy_indices])
            eigenvalues[noisy_indices] = avg_noisy_eigenvalue
        cleaned_corr = eigenvectors @ np.diag(eigenvalues) @ eigenvectors.T
        diag = np.diag(cleaned_corr)
        scaling_matrix = np.diag(1.0 / np.sqrt(diag))
        scaled_corr = scaling_matrix @ cleaned_corr @ scaling_matrix
        return pd.DataFrame(scaled_corr, index=returns_df.columns, columns=returns_df.columns)

    @staticmethod
    def get_eigen_portfolio_weights(returns_df: pd.DataFrame) -> pd.Series:
        T, N = returns_df.shape
        corr = returns_df.corr().fillna(0).values
        eigenvalues, eigenvectors = np.linalg.eigh(corr)
        dominant_vector = eigenvectors[:, np.argmax(eigenvalues)]
        abs_weights = np.abs(dominant_vector)
        normalized_weights = abs_weights / np.sum(abs_weights)
        return pd.Series(normalized_weights, index=returns_df.columns)