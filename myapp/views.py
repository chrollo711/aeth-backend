from rest_framework import generics
from .models import GPSData
from .serializers import GPSDataSerializer
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
from django.shortcuts import render

def dashboard(request):
    return render(request, 'home.html')


@method_decorator(csrf_exempt, name='dispatch')
class GPSDataListCreate(generics.ListCreateAPIView):
    queryset = GPSData.objects.all()
    serializer_class = GPSDataSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            
            # Simple ML prediction - predict next speed based on last 5 entries
            last_5 = GPSData.objects.order_by('-timestamp')[:5]
            if len(last_5) >= 3:  # Need at least 3 points for prediction
                df = pd.DataFrame(list(last_5.values('speed', 'timestamp')))
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df['time_ordinal'] = df['timestamp'].apply(lambda x: x.toordinal())
                
                X = df['time_ordinal'].values.reshape(-1, 1)
                y = df['speed'].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                next_time = df['time_ordinal'].iloc[-1] + 1
                predicted_speed = model.predict(np.array([[next_time]]))[0]
                
                return Response({
                    'data': serializer.data,
                    'prediction': {
                        'next_speed': round(float(predicted_speed), 2),
                        'message': 'Speed may increase' if predicted_speed > y[-1] else 'Speed may decrease'
                    }
                }, status=status.HTTP_201_CREATED)
            
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)