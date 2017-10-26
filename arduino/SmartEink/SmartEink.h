/* Arduino Smart_Eink Library 
 * Copyright (C) 2016 by NOA Labs
 * Author  Bruce Guo (NOA Labs)
 *
 * This file is work for Eink.
 *
 * This Library is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This Library is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this Library. If not, see
 * <http://www.gnu.org/licenses/>.
 */


#ifndef SmartEink_h
#define SmartEink_h
 
#ifndef INT8U
#define INT8U unsigned char
#endif
#ifndef INT16U
#define INT16U unsigned int
#endif
#ifndef INT32U
#define INT32U unsigned long
#endif
#if defined(__AVR_ATmega1280__) || defined(__AVR_ATmega2560__)

#define Eink_CS1_LOW  {DDRH |= 0x08;PORTH &=~ 0x08;}
#define Eink_CS1_HIGH {DDRH |= 0x08;PORTH |=  0x08;}
#define Eink_DC_LOW   {DDRE |= 0x08;PORTE &=~ 0x08;}
#define Eink_DC_HIGH  {DDRE |= 0x08;PORTE |=  0x08;} 
 
#elif defined(__AVR_ATmega32U4__)

#define Eink_CS1_LOW  {DDRD |= 0x80;PORTD &=~ 0x80;}
#define Eink_CS1_HIGH {DDRD |= 0x80;PORTD |=  0x80;}
#define Eink_DC_LOW   {DDRC |= 0x40;PORTC &=~ 0x40;}
#define Eink_DC_HIGH  {DDRC |= 0x40;PORTC |=  0x40;}

#else

#define Eink_CS1_LOW  {DDRD |= 0x40;PORTD &=~ 0x40;}
#define Eink_CS1_HIGH {DDRD |= 0x40;PORTD |=  0x40;}
#define Eink_DC_LOW   {DDRD |= 0x20;PORTD &=~ 0x20;}
#define Eink_DC_HIGH  {DDRD |= 0x20;PORTD |=  0x20;}


#endif
class E_ink
{
public:
 void  InitEink(void);
 void ClearScreen(void);
 void EinkShowLogo(INT8U *image);
 void ShowBitMap(INT8U *image);
 void RefreshScreen(void);
 void GetCharMatrixData(INT16U unicodeChar);
 void ConverCharMatrixData (void);
 void ConverChineseMatrixData(void);
 void DisplayChar(INT8U x1,INT8U y1,INT16U unicodeChar);
 void DisplayTwoDimensionalCode(INT8U x,INT8U y);
 void EinkP8x16Str(INT8U y,INT8U x,char ch[]);
 
private:
 INT8U matrixData[32];
 INT8U matrixDataConver[200]; 
 INT8U GetTwoByte(INT8U image);
 void  WriteComm(INT8U command);
 void  WriteData(INT8U data);
 INT16U  GTRead(INT32U address);
 INT16U ConvertData(INT8U originalData); 
 void  ConverDimensionalCode(void);
 

 void  CloseBump(void);
 void  ConfigureLUTRegister(void);
 void  SetPositionXY(INT8U Xs, INT8U Xe,INT8U Ys,INT8U Ye);
 
};

#endif
/*********************************************************************************************************
  END FILE
*********************************************************************************************************/
  
