apiVersion: apps/v1
kind: Deployment
metadata:
  name: __NAME__-service
  namespace: microapp
spec:
  replicas: 2
  selector:
    matchLabels:
      app: __NAME__
  template:
    metadata:
      labels:
        app: __NAME__
    spec:
      restartPolicy: Always
      initContainers:
        - name: esperar-mysql
          image: busybox:1.36
          command: ["sh", "-c", "until nc -z mysql-__NAME__ 3306; do echo esperando mysql; sleep 3; done"]
      containers:
        - name: __NAME__
          image: adominguez1/__NAME__-service:latest
          ports:
            - containerPort: __PORT__
          env:
            - name: MYSQL_HOST
              value: mysql-__NAME__
            - name: MYSQL_USER
              value: root
            - name: MYSQL_DB
              value: __NAME___db
            - name: MYSQL_PASSWORD
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: __NAME__-db-password
            - name: SECRET_KEY
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: secret-key
            - name: CONSUL_ENABLED
              value: "false"
__EXTRA__
          readinessProbe:
            httpGet:
              path: /health
              port: __PORT__
            initialDelaySeconds: 5
            periodSeconds: 5
          resources:
            requests:
              cpu: "50m"
              memory: "64Mi"
            limits:
              memory: "256Mi"
---
apiVersion: v1
kind: Service
metadata:
  name: __NAME__-svc
  namespace: microapp
spec:
  type: ClusterIP
  selector:
    app: __NAME__
  ports:
    - port: __PORT__
      targetPort: __PORT__
