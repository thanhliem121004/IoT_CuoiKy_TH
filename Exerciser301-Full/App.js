import React, { useState, useEffect } from 'react';
import axios from 'axios';
import {
  Card,
  Container,
  Typography,
  Switch,
  ButtonGroup,
  Button,
  CircularProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Box,
  Grid,
  TextField,
  Divider,
  IconButton,
  Tooltip,
  Avatar,
  Fab,
  Paper
} from '@mui/material';
import {
  LightbulbOutlined,
  Sensors,
  Toys,
  Refresh,
  AddCircleOutline,
  Delete,
  Menu as MenuIcon,
  Search as SearchIcon
} from '@mui/icons-material';
import { motion } from 'framer-motion';
import { SnackbarProvider, useSnackbar } from 'notistack';

// ⚙️ Backend API
const API_URL = 'http://localhost:8080/api/devices';

function IoTPanel() {
  const { enqueueSnackbar } = useSnackbar();
  const [darkMode, setDarkMode] = useState(false);
  const [devices, setDevices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [newDevice, setNewDevice] = useState({ name: '', topic: '', type: 'LED' });

  // --- Hàm tải danh sách thiết bị ---
  const fetchDevices = React.useCallback(async () => {
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
  }, [enqueueSnackbar]);

  useEffect(() => {
    fetchDevices();
    const interval = setInterval(fetchDevices, 4000); // tự động refresh
    return () => clearInterval(interval);
  }, [fetchDevices]);

  useEffect(() => {
    document.body.classList.toggle('dark', darkMode);
  }, [darkMode]);

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

  // --- Giao diện chính (modern dashboard) ---
  return (
    <Box className="app-root">
  <Box className="sidebar">
        <Box className="brand">
          <Avatar src="/logo192.png" sx={{ width: 48, height: 48, mr: 1 }} />
          <Box>
            <Typography variant="h6" fontWeight={700}>Exerciser301</Typography>
            <Typography variant="caption" color="text.secondary">IoT Dashboard</Typography>
          </Box>
        </Box>

        <Box mt={4} className="nav">
          <Button startIcon={<LightbulbOutlined />} fullWidth sx={{ justifyContent: 'flex-start' }}>
            Devices
          </Button>
          <Button startIcon={<Sensors />} fullWidth sx={{ justifyContent: 'flex-start', mt: 1 }}>
            Sensors
          </Button>
          <Button startIcon={<Toys />} fullWidth sx={{ justifyContent: 'flex-start', mt: 1 }}>
            Actuators
          </Button>
        </Box>

        <Box sx={{ mt: 'auto', mb: 2 }}>
          <Typography variant="caption" color="text.secondary">Auto refresh every 4s</Typography>
          <Box display="flex" gap={1} mt={1} alignItems="center">
            <IconButton color="primary" onClick={fetchDevices}><Refresh /></IconButton>
            <Box sx={{ ml: 1 }}>
              <Typography variant="caption" color="inherit">Theme</Typography>
              <Switch checked={darkMode} onChange={(e) => setDarkMode(e.target.checked)} size="small" />
            </Box>
          </Box>
        </Box>
      </Box>

      <Box className="content">
        <Paper elevation={0} className="headerPaper">
          <Box display="flex" alignItems="center" justifyContent="space-between" width="100%">
            <Box display="flex" alignItems="center" gap={2}>
              <IconButton size="large" className="menuBtn"><MenuIcon /></IconButton>
              <Typography variant="h5" fontWeight={700}>Control Panel</Typography>
              <Typography variant="body2" color="text.secondary">Manage your IoT devices</Typography>
            </Box>

            <Box display="flex" alignItems="center" gap={2}>
              <Paper component="form" className="searchBox" elevation={0}>
                <IconButton type="button" sx={{ p: '10px' }} aria-label="search"><SearchIcon /></IconButton>
                <InputLabel shrink={false} sx={{ display: 'none' }}>Search</InputLabel>
                <TextField
                  placeholder="Tìm theo tên hoặc topic..."
                  variant="standard"
                  InputProps={{ disableUnderline: true }}
                  onChange={(e) => {/* keep for future filter */}}
                />
              </Paper>
              <Tooltip title="Refresh">
                <IconButton onClick={fetchDevices}><Refresh /></IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Paper>

        <Box mt={3}>
          <Card className="quickAdd" sx={{ p: 2, mb: 3 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  label="Tên thiết bị"
                  fullWidth
                  value={newDevice.name}
                  onChange={(e) => setNewDevice({ ...newDevice, name: e.target.value })}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <TextField
                  label="MQTT Topic"
                  fullWidth
                  value={newDevice.topic}
                  onChange={(e) => setNewDevice({ ...newDevice, topic: e.target.value })}
                />
              </Grid>
              <Grid item xs={8} md={3}>
                <FormControl fullWidth>
                  <InputLabel>Loại</InputLabel>
                  <Select
                    value={newDevice.type}
                    label="Loại"
                    onChange={(e) => setNewDevice({ ...newDevice, type: e.target.value })}
                  >
                    <MenuItem value="LED">LED</MenuItem>
                    <MenuItem value="MOTOR">Motor</MenuItem>
                    <MenuItem value="SENSOR">Sensor</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={4} md={1}>
                <Fab color="primary" size="small" onClick={createDevice} aria-label="add">
                  <AddCircleOutline />
                </Fab>
              </Grid>
            </Grid>
          </Card>

          {devices.length === 0 ? (
            <Typography align="center" color="text.secondary">Không có thiết bị nào — thêm thiết bị để bắt đầu.</Typography>
          ) : (
            <Grid container spacing={3}>
              {devices.map((d) => (
                <Grid item xs={12} sm={6} md={4} key={d.id}>
                  <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
                    <Card className={`deviceCard ${d.type?.toLowerCase()}`} sx={{ p: 2 }}>
                      <Box display="flex" alignItems="center" justifyContent="space-between">
                        <Box>
                          <Typography variant="subtitle1" fontWeight={700}>{d.name}</Typography>
                          <Typography variant="caption" color="text.secondary">{d.topic ?? ''} • {d.type}</Typography>
                          <Box className="statusRow">
                            {d.type === 'LED' && <span className={`chip ${d.ledState ? 'chip--ok' : 'chip--warn'}`}>{d.ledState ? 'ON' : 'OFF'}</span>}
                            {d.type === 'MOTOR' && <span className={`chip ${d.motorState === 0 ? 'chip--info' : 'chip--ok'}`}>State: {d.motorState}</span>}
                            {d.type === 'SENSOR' && <span className="chip chip--info">Sensor</span>}
                          </Box>
                        </Box>
                        <Box display="flex" alignItems="center" gap={1}>
                          {d.type === 'LED' && <LightbulbOutlined color="warning" />}
                          {d.type === 'MOTOR' && <Toys color="success" />}
                          {d.type === 'SENSOR' && <Sensors color="info" />}
                          <Tooltip title="Xoá">
                            <IconButton color="error" onClick={() => deleteDevice(d.id)}><Delete /></IconButton>
                          </Tooltip>
                        </Box>
                      </Box>

                      <Divider sx={{ my: 1 }} />

                      {d.type === 'LED' && (
                        <Box display="flex" alignItems="center" justifyContent="space-between">
                          <Typography>LED</Typography>
                          <Box display="flex" alignItems="center" gap={1}>
                            <Switch checked={!!d.ledState} color="warning" onChange={(e) => toggleLed(d.id, e.target.checked)} />
                            <Typography variant="body2" color={d.ledState ? 'orange' : 'text.secondary'} fontWeight={700}>{d.ledState ? 'BẬT' : 'TẮT'}</Typography>
                          </Box>
                        </Box>
                      )}

                      {d.type === 'MOTOR' && (
                        <Box display="flex" alignItems="center" justifyContent="space-between">
                          <Typography>Motor</Typography>
                          <ButtonGroup>
                            <Button variant={d.motorState === -1 ? 'contained' : 'outlined'} onClick={() => toggleMotor(d.id, -1)}>Lùi</Button>
                            <Button variant={d.motorState === 0 ? 'contained' : 'outlined'} onClick={() => toggleMotor(d.id, 0)}>Dừng</Button>
                            <Button variant={d.motorState === 1 ? 'contained' : 'outlined'} onClick={() => toggleMotor(d.id, 1)}>Tiến</Button>
                          </ButtonGroup>
                        </Box>
                      )}

                      {d.type === 'SENSOR' && (
                        <Box>
                          <Typography variant="body2">🌡️ Nhiệt độ: <b>{d.temperature?.toFixed(1) ?? '--'}</b> °C</Typography>
                          <Typography variant="body2">💧 Độ ẩm: <b>{d.humidity?.toFixed(1) ?? '--'}</b> %</Typography>
                        </Box>
                      )}
                    </Card>
                  </motion.div>
                </Grid>
              ))}
            </Grid>
          )}
        </Box>
      </Box>
    </Box>
  );
}

export default function App() {
  return (
    <SnackbarProvider maxSnack={3} autoHideDuration={2500}>
      <IoTPanel />
    </SnackbarProvider>
  );
}
