/* Arduino Smart_Eink Library 
 * Copyright (C) 2016 by NOA Labs
 * Author  Bruce Guo (NOA Labs)
 *
 * This file is E-ink demo showing string.
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
/*
D/C ~ D5
CS ~ D6
BUSY ~ D7
BS ~ D8
MOSI ~ D11
MISO ~ D12
CLK ~ D13

*/


 
#include <SmartEink.h>
#include <SPI.h>

E_ink Eink;

void setup()
{
  //BS LOW for 4 line SPI
  pinMode(8,OUTPUT);
  digitalWrite(8, LOW);
  
Eink.InitEink();

Eink.ClearScreen();// clear the screen

Eink.EinkP8x16Str(14,8,"NOA-Labs.com");
Eink.EinkP8x16Str(10,8,"smart-prototyping.com");
Eink.EinkP8x16Str(6,8,"0123456789");
Eink.EinkP8x16Str(2,8,"ABCDEFG abcdefg");

Eink.RefreshScreen(); 
}
void loop()
{ 

}

