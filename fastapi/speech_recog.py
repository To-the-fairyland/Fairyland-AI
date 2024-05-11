import torch
import torch.nn as nn
import librosa
import numpy as np
import torchaudio
import os

EMOTIONS = {1:'neutral', 2:'calm', 3:'happy', 4:'sad', 5:'angry', 6:'fear', 7:'disgust', 0:'surprise'} # surprise je promenjen sa 8 na 0

class TimeDistributed(nn.Module):
    def __init__(self, module):
        super(TimeDistributed, self).__init__()
        self.module = module

    def forward(self, x):

        if len(x.size()) <= 2:
            return self.module(x)
        # squash samples and timesteps into a single axis
        elif len(x.size()) == 3:  # (samples, timesteps, inp1)
            x_reshape = x.contiguous().view(-1, x.size(2))  # (samples * timesteps, inp1)
        elif len(x.size()) == 4:  # (samples,timesteps,inp1,inp2)
            x_reshape = x.contiguous().view(-1, x.size(2), x.size(3))  # (samples*timesteps,inp1,inp2)
        else:  # (samples,timesteps,inp1,inp2,inp3)
            x_reshape = x.contiguous().view(-1, x.size(2), x.size(3), x.size(4))  # (samples*timesteps,inp1,inp2,inp3)

        y = self.module(x_reshape)

        # we have to reshape Y
        if len(x.size()) == 3:
            y = y.contiguous().view(x.size(0), -1, y.size(1))  # (samples, timesteps, out1)
        elif len(x.size()) == 4:
            y = y.contiguous().view(x.size(0), -1, y.size(1), y.size(2))  # (samples, timesteps, out1,out2)
        else:
            y = y.contiguous().view(x.size(0), -1, y.size(1), y.size(2),
                                    y.size(3))  # (samples, timesteps, out1,out2, out3)
        return y


class HybridModel(nn.Module):
    def __init__(self, num_emotions):
        super().__init__()
        # conv block
        self.conv2Dblock = nn.Sequential(
            # 1. conv block
            TimeDistributed(nn.Conv2d(in_channels=1,
                                      out_channels=16,
                                      kernel_size=3,
                                      stride=1,
                                      padding=1
                                      )),
            TimeDistributed(nn.BatchNorm2d(16)),
            TimeDistributed(nn.ReLU()),
            TimeDistributed(nn.MaxPool2d(kernel_size=2, stride=2)),
            TimeDistributed(nn.Dropout(p=0.3)),
            # 2. conv block
            TimeDistributed(nn.Conv2d(in_channels=16,
                                      out_channels=32,
                                      kernel_size=3,
                                      stride=1,
                                      padding=1
                                      )),
            TimeDistributed(nn.BatchNorm2d(32)),
            TimeDistributed(nn.ReLU()),
            TimeDistributed(nn.MaxPool2d(kernel_size=4, stride=4)),
            TimeDistributed(nn.Dropout(p=0.3)),
            # 3. conv block
            TimeDistributed(nn.Conv2d(in_channels=32,
                                      out_channels=64,
                                      kernel_size=3,
                                      stride=1,
                                      padding=1
                                      )),
            TimeDistributed(nn.BatchNorm2d(64)),
            TimeDistributed(nn.ReLU()),
            TimeDistributed(nn.MaxPool2d(kernel_size=4, stride=4)),
            TimeDistributed(nn.Dropout(p=0.3))
        )
        # LSTM block
        hidden_size = 64
        self.lstm = nn.LSTM(input_size=1024, hidden_size=hidden_size, bidirectional=True, batch_first=True)
        self.dropout_lstm = nn.Dropout(p=0.4)
        self.attention_linear = nn.Linear(2 * hidden_size, 1)  # 2*hidden_size for the 2 outputs of bidir LSTM
        # Linear softmax layer
        self.out_linear = nn.Linear(2 * hidden_size, num_emotions)

    def forward(self, x):
        conv_embedding = self.conv2Dblock(x)
        conv_embedding = torch.flatten(conv_embedding, start_dim=2)  # do not flatten batch dimension and time
        lstm_embedding, (h, c) = self.lstm(conv_embedding)
        lstm_embedding = self.dropout_lstm(lstm_embedding)
        # lstm_embedding (batch, time, hidden_size*2)
        batch_size, T, _ = lstm_embedding.shape
        attention_weights = [None] * T
        for t in range(T):
            embedding = lstm_embedding[:, t, :]
            attention_weights[t] = self.attention_linear(embedding)
        attention_weights_norm = nn.functional.softmax(torch.stack(attention_weights, -1), dim=-1)
        attention = torch.bmm(attention_weights_norm, lstm_embedding)  # (Bx1xT)*(B,T,hidden_size*2)=(B,1,2*hidden_size)
        attention = torch.squeeze(attention, 1)
        output_logits = self.out_linear(attention)
        output_softmax = nn.functional.softmax(output_logits, dim=1)
        return output_logits, output_softmax, attention_weights_norm

def getMELspectrogram(audio, sample_rate):
    mel_spec = librosa.feature.melspectrogram(y=audio,
                                              sr=sample_rate,
                                              n_fft=1024,
                                              win_length = 512,
                                              window='hamming',
                                              hop_length = 256,
                                              n_mels=128,
                                              fmax=sample_rate/2
                                             )
    mel_spec_db = librosa.power_to_db(mel_spec, ref=np.max)
    return mel_spec_db


def splitIntoChunks(mel_spec,win_size,stride):
    t = mel_spec.shape[1]
    num_of_chunks = int(t/stride)
    chunks = []
    for i in range(num_of_chunks):
        chunk = mel_spec[:,i*stride:i*stride+win_size]
        if chunk.shape[1] == win_size:
            chunks.append(chunk)
    return np.stack(chunks,axis=0)

def load_model():
    LOAD_PATH = os.path.join(os.getcwd(), 'models')
    model = HybridModel(len(EMOTIONS))
    model.load_state_dict(torch.load(os.path.join(LOAD_PATH, 'best_cnn_attention_lstm_model.pt')))
    return model

def predict(filename):

    model = load_model()    ### ISSUE : 서버 상에서 어떻게 모델을 계속 load 된 채로 유지하지?

    SAMPLE_RATE = 48000
    audio, sample_rate = librosa.load(filename, duration=3, offset=0.5, sr=SAMPLE_RATE)
    signal = np.zeros((int(SAMPLE_RATE * 3, )))
    signal[:len(audio)] = audio

    mel = getMELspectrogram(signal, SAMPLE_RATE)
    librosa.display.specshow(mel, y_axis='mel', x_axis='time')
    chunks = splitIntoChunks(mel, win_size=128, stride=64)
    audio_tensor = torch.from_numpy(chunks)

    audio_tensor = torch.unsqueeze(audio_tensor, dim=1).float()
    audio_tensor = torch.unsqueeze(audio_tensor, dim=0).float()
    output_logits, output_softmax, attention_weights_norm = model(audio_tensor)
    predictions = torch.argmax(output_softmax, dim=1)
    emotion = EMOTIONS[int(predictions[0])]
    return emotion

