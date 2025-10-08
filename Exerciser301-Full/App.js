import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Card, Container, Typography, Switch, ButtonGroup, Button,
  CircularProgress, Select, MenuItem, FormControl, InputLabel,
  Box, Grid, TextField, Divider, IconButton, Tooltip
} from '@mui/material';
import {
  LightbulbOutlined, Sensors, Toys, Refresh, AddCircleOutline, Delete
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { SnackbarProvider, useSnackbar } from 'notistack';

// ⚙️ Backend API
const API_URL = 'http://localhost:8080/api/devices';

function IoTPanel() {
  const { enqueueSnackbar } = useSnackbar();
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newDevice, setNewDevice] = useState({ name: '', topic: '', type: 'LED' });

  // --- Hàm tải danh sách thiết bị ---
  const fetchDevices = async () => {
    try {
      const res = await axios.get(API_URL);
      const data = res.data;
      if (Array.isArray(data)) setDevices(data);
      else if (data?.content && Array.isArray(data.content)) setDevices(data.content);
      else setDevices([]);
    } catch (err) {
      console.error('Lỗi tải thiết bị:', err);
      enqueueSnackbar('⚠️ Không thể tải danh sách thiết bị!', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 4000); // tự động refresh
    return () => clearInterval(interval);
  }, []);

  // --- Điều khiển LED ---
  const toggleLed = async (id, newState) => {
    try {
      await axios.post(`${API_URL}/${id}/led`, { on: !!newState });
      enqueueSnackbar(`💡 LED ${newState ? 'bật' : 'tắt'}`, { variant: 'success' });
      fetchDevices();
    } catch {
      enqueueSnackbar('❌ Không thể điều khiển đèn LED!', { variant: 'error' });
    }
  };

  // --- Điều khiển Motor ---
  const toggleMotor = async (id, state) => {
    try {
      await axios.post(`${API_URL}/${id}/motor`, { state });
      enqueueSnackbar(`⚙️ Motor ${state === 1 ? 'Tiến' : state === -1 ? 'Lùi' : 'Dừng'}`, {
        variant: 'info'
      });
      fetchDevices();
    } catch {
      enqueueSnackbar('❌ Không thể điều khiển động cơ!', { variant: 'error' });
    }
  };

  // --- Thêm thiết bị mới ---
  const createDevice = async () => {
    if (!newDevice.name.trim() || !newDevice.topic.trim()) {
      enqueueSnackbar('⚠️ Vui lòng nhập đầy đủ tên và topic!', { variant: 'warning' });
      return;
    }
    try {
      await axios.post(API_URL, newDevice);
      enqueueSnackbar('✅ Đã thêm thiết bị mới!', { variant: 'success' });
      setNewDevice({ name: '', topic: '', type: 'LED' });
      fetchDevices();
    } catch (err) {
      enqueueSnackbar('❌ Không thể thêm thiết bị!', { variant: 'error' });
    }
  };

  // --- Xoá thiết bị ---
  const deleteDevice = async (id) => {
    if (!window.confirm('⚠️ Bạn có chắc muốn xoá thiết bị này không?')) return;
    try {
      await axios.delete(`${API_URL}/${id}`);
      enqueueSnackbar('🗑️ Đã xoá thiết bị!', { variant: 'success' });
      fetchDevices();
    } catch {
      enqueueSnackbar('❌ Không thể xoá thiết bị!', { variant: 'error' });
    }
  };

  // --- Hiển thị trạng thái tải ---
  if (loading && devices.length === 0) {
    return (
      <Container maxWidth="sm" sx={{ textAlign: 'center', mt: 8 }}>
        <CircularProgress />
        <Typography mt={2}>🔌 Đang kết nối đến máy chủ IoT...</Typography>
      </Container>
    );
  }

  // --- Giao diện chính ---
  return (
    <Container maxWidth="md" sx={{ py: 4 }}>
      {/* Header */}
      <Box display="flex" alignItems="center" justifyContent="space-between" mb={3}>
        <Typography variant="h4" fontWeight={700}>
          💡 IoT Control Panel
        </Typography>
        <Tooltip title="Làm mới dữ liệu">
          <IconButton color="primary" onClick={fetchDevices}>
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* Form thêm thiết bị */}
      <Card sx={{ p: 3, mb: 4, boxShadow: 3, borderRadius: 3 }}>
        <Typography variant="h6" gutterBottom>➕ Thêm thiết bị mới</Typography>
        <Grid container spacing={2}>
          <Grid item xs={12} sm={4}>
            <TextField
              label="Tên thiết bị"
              fullWidth
              value={newDevice.name}
              onChange={(e) => setNewDevice({ ...newDevice, name: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={4}>
            <TextField
              label="MQTT Topic"
              fullWidth
              value={newDevice.topic}
              onChange={(e) => setNewDevice({ ...newDevice, topic: e.target.value })}
            />
          </Grid>
          <Grid item xs={12} sm={3}>
            <FormControl fullWidth>
              <InputLabel>Loại thiết bị</InputLabel>
              <Select
                value={newDevice.type}
                label="Loại thiết bị"
                onChange={(e) => setNewDevice({ ...newDevice, type: e.target.value })}
              >
                <MenuItem value="LED">💡 LED</MenuItem>
                <MenuItem value="MOTOR">⚙️ Motor</MenuItem>
                <MenuItem value="SENSOR">🌡️ Cảm biến</MenuItem>
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} sm={1} display="flex" alignItems="center" justifyContent="center">
            <IconButton color="success" onClick={createDevice}>
              <AddCircleOutline fontSize="large" />
            </IconButton>
          </Grid>
        </Grid>
      </Card>

      {/* Danh sách thiết bị */}
      {devices.length === 0 ? (
        <Typography align="center" color="text.secondary">
          ⚙️ Chưa có thiết bị nào, hãy thêm mới!
        </Typography>
      ) : (
        devices.map((d) => (
          <motion.div
            key={d.id}
            initial={{ opacity: 0, y: 15 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
          >
            <Card
              sx={{
                p: 3,
                mb: 3,
                borderRadius: 3,
                boxShadow: 4,
                background:
                  d.type === 'LED'
                    ? '#fffde7'
                    : d.type === 'MOTOR'
                      ? '#e8f5e9'
                      : '#e3f2fd',
              }}
            >
              <Box display="flex" alignItems="center" justifyContent="space-between">
                <Box>
                  <Typography variant="h6" fontWeight={600}>
                    {d.name}{' '}
                    <Typography component="span" color="text.secondary" fontSize={14}>
                      ({d.type})
                    </Typography>
                  </Typography>
                </Box>
                <Box display="flex" alignItems="center" gap={1}>
                  {d.type === 'LED' && <LightbulbOutlined color="warning" />}
                  {d.type === 'MOTOR' && <Toys color="success" />}
                  {d.type === 'SENSOR' && <Sensors color="info" />}
                  <Tooltip title="Xoá thiết bị">
                    <IconButton color="error" onClick={() => deleteDevice(d.id)}>
                      <Delete />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>

              <Divider sx={{ my: 2 }} />

              {d.type === 'LED' && (
                <Box display="flex" alignItems="center" gap={2}>
                  <Typography>LED:</Typography>
                  <Switch
                    checked={!!d.ledState}
                    color="warning"
                    onChange={(e) => toggleLed(d.id, e.target.checked)}
                  />
                  <Typography fontWeight={600} color={d.ledState ? 'orange' : 'grey'}>
                    {d.ledState ? 'BẬT' : 'TẮT'}
                  </Typography>
                </Box>
              )}

              {d.type === 'MOTOR' && (
                <Box display="flex" alignItems="center" gap={2}>
                  <Typography>Động cơ:</Typography>
                  <ButtonGroup variant="outlined" size="small">
                    <Button
                      variant={d.motorState === -1 ? 'contained' : 'outlined'}
                      color="secondary"
                      onClick={() => toggleMotor(d.id, -1)}
                    >
                      Lùi
                    </Button>
                    <Button
                      variant={d.motorState === 0 ? 'contained' : 'outlined'}
                      color="inherit"
                      onClick={() => toggleMotor(d.id, 0)}
                    >
                      Dừng
                    </Button>
                    <Button
                      variant={d.motorState === 1 ? 'contained' : 'outlined'}
                      color="success"
                      onClick={() => toggleMotor(d.id, 1)}
                    >
                      Tiến
                    </Button>
                  </ButtonGroup>
                </Box>
              )}

              {d.type === 'SENSOR' && (
                <Box sx={{ color: '#333', lineHeight: 1.8 }}>
                  🌡️ Nhiệt độ: <b>{d.temperature?.toFixed(1) ?? '--'}</b> °C<br />
                  💧 Độ ẩm: <b>{d.humidity?.toFixed(1) ?? '--'}</b> %
                </Box>
              )}
            </Card>
          </motion.div>
        ))
      )}
    </Container>
  );
}

export default function App() {
  return (
    <SnackbarProvider maxSnack={3} autoHideDuration={2500}>
      <IoTPanel />
    </SnackbarProvider>
  );
}
