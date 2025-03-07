import copy
import crcmod
from selfdrive.car.nissan.values import CAR

nissan_checksum = crcmod.mkCrcFun(0x11d, initCrc=0x00, rev=False, xorOut=0xff)


def create_steering_control(packer, car_fingerprint, apply_steer, frame, steer_on, lkas_max_torque):
  if car_fingerprint == CAR.XTRAIL:
    idx = (frame % 16)
    values = {
      "DESIRED_ANGLE": apply_steer,
      "SET_0x80_2": 0x80,
      "SET_0x80": 0x80,
      "MAX_TORQUE": lkas_max_torque if steer_on else 0,
      "COUNTER": idx,
      "LKA_ACTIVE": steer_on,
    }

    dat = packer.make_can_msg("LKAS", 0, values)[2]

    values["CHECKSUM"] = nissan_checksum(dat[:7])

  return packer.make_can_msg("LKAS", 0, values)


def create_acc_cancel_cmd(packer, cruise_throttle_msg, frame):
  values = copy.copy(cruise_throttle_msg)

  values["CANCEL_BUTTON"] = 1
  values["NO_BUTTON_PRESSED"] = 0
  values["PROPILOT_BUTTON"] = 0
  values["SET_BUTTON"] = 0
  values["RES_BUTTON"] = 0
  values["FOLLOW_DISTANCE_BUTTON"] = 0
  values["COUNTER"] = (frame % 4)

  return packer.make_can_msg("CRUISE_THROTTLE", 2, values)


def create_lkas_hud_msg(packer, lkas_hud_msg, enabled, left_line, right_line, left_lane_depart, right_lane_depart):
  values = lkas_hud_msg

  values["RIGHT_LANE_YELLOW_FLASH"] = 1 if right_lane_depart else 0
  values["LEFT_LANE_YELLOW_FLASH"] = 1 if left_lane_depart else 0

  values["LARGE_STEERING_WHEEL_ICON"] = 2 if enabled else 0
  values["RIGHT_LANE_GREEN"] = 1 if right_line and enabled else 0
  values["LEFT_LANE_GREEN"] = 1 if left_line and enabled else 0

  return packer.make_can_msg("PROPILOT_HUD", 0, values)


def create_lkas_hud_info_msg(packer, lkas_hud_info_msg, steer_hud_alert):
  values = lkas_hud_info_msg

  if steer_hud_alert:
    values["HANDS_ON_WHEEL_WARNING"] = 1

  return packer.make_can_msg("PROPILOT_HUD_INFO_MSG", 0, values)
