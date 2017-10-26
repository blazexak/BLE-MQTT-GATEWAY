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


#ifndef BeanSmartEinkOpt_h
#define BeanSmartEinkOpt_h
 
#ifndef INT8U
#define INT8U unsigned char
#endif
#ifndef INT16U
#define INT16U unsigned int
#endif
#ifndef INT32U
#define INT32U unsigned long
#endif

// #if defined(__AVR_ATmega32U4__)

// #define Eink_CS1_LOW  {DDRD |= 0x80;PORTD &=~ 0x80;}
// #define Eink_CS1_HIGH {DDRD |= 0x80;PORTD |=  0x80;}
// #define Eink_DC_LOW   {DDRC |= 0x40;PORTC &=~ 0x40;}
// #define Eink_DC_HIGH  {DDRC |= 0x40;PORTC |=  0x40;}

// #else

// #define Eink_CS1_LOW  {DDRB |= 0x02;PORTB &=~ 0x02;} // BEAN+ D5: PortB Bit Mask 2
// #define Eink_CS1_HIGH {DDRB |= 0x02;PORTB |=  0x02;}
// #define Eink_DC_LOW   {DDRD |= 0x40;PORTD &=~ 0x40;} // BEAN+ D2: PortB Bit Mask 1
// #define Eink_DC_HIGH  {DDRD |= 0x40;PORTD |=  0x40;}
// #define Eink_CS1_LOW  {DDRD |= 0x01;PORTD &=~ 0x01;} // BEAN D0: PortB Bit Mask 2, 0
// #define Eink_CS1_HIGH {DDRD |= 0x01;PORTD |=  0x01;}
// #define Eink_DC_LOW   {DDRD |= 0x02;PORTD &=~ 0x02;} // BEAN D1: PortB Bit Mask 1, 1
// #define Eink_DC_HIGH  {DDRD |= 0x02;PORTD |=  0x02;}

// #endif
class E_ink
{
public:
 void InitEink(void); //keep
 void ClearScreen(void); //keep
 void RefreshScreen(void); //keep
 void GetCharMatrixData(INT16U unicodeChar); //keep
 void ConverCharMatrixData (void); // keep
 void DisplayChar(INT8U x1,INT8U y1,INT16U unicodeChar); //keep
 void EinkP8x16Str(INT8U y,INT8U x,char ch[]); //keep
 
private:
 INT8U matrixData[32]; //keep
 INT8U matrixDataConver[200];  //keep
 void  WriteComm(INT8U command); //keep
 void  WriteData(INT8U data); //keep
 INT16U ConvertData(INT8U originalData); //keep
 

 void  CloseBump(void); //keep
 void  ConfigureLUTRegister(void); //keep
 void  SetPositionXY(INT8U Xs, INT8U Xe,INT8U Ys,INT8U Ye); //keep
 
};

#endif
/*********************************************************************************************************
  END FILE
*********************************************************************************************************/
  
