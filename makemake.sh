# **************************************************************************** #
#                                                                              #
#                                                         :::      ::::::::    #
#    makemake.sh                                        :+:      :+:    :+:    #
#                                                     +:+ +:+         +:+      #
#    By: jaguillo <jaguillo@student.42.fr>          +#+  +:+       +#+         #
#                                                 +#+#+#+#+#+   +#+            #
#    Created: 2015/04/07 22:29:29 by jaguillo          #+#    #+#              #
#    Updated: 2015/04/11 19:36:25 by jaguillo         ###   ########.fr        #
#                                                                              #
# **************************************************************************** #

#
# Config
#

function prompt()
{
	if [[ ! -z "$2" ]]; then
		MSG="$1 ($2)"
	else
		MSG="$1"
	fi
	read -p "> $MSG: " R
	if [[ ! -z "$2" ]]; then
		if [[ -z "$R" ]]; then
			R="$2"
		fi
	fi
	echo "$R"
};

echo "---> Executable name <---"
NAME=`prompt "NAME"`

echo "---> Directories <---"
C_DIR=`prompt "Sources directory" "."`
H_DIRS=`prompt "Headers directory" "."`
O_DIR=`prompt "Objects directory" "o"`

echo "---> Makefiles to call <---"
LIBS=`prompt "Libraries" ""`

echo "---> Compilation <---"
CC=`prompt "Compiler" "clang++"`
FLAGS=`prompt "Flags" "-Wall -Wextra -Werror -O2"`

echo "---> Links (-L and -l) <---"
DEF=""
for L in $LIBS; do
	DEF="-L$L $DEF"
done
LINKS=`prompt "Libraries links" "$DEF"`

echo "---> Headers (-I) <---"
DEF=""
for H in $H_DIRS; do
	DEF="-I$H $DEF"
done
for L in $LIBS; do
	DEF="-I$L $DEF"
done
HEADS=`prompt "Headers links" "$DEF"`

echo "---> Advenced config <---"
if [[ "`prompt "More config" "No"`" != "No" ]]; then
	echo "Sorry, No more config"
fi

#
# Generation
#

function includes()
{
	INCLUDES="`cat $1 | grep "#include "'"' | sed -E 's/#include "([^"]+)"/\1/' | tr '\n' ' '`"
	for H in $INCLUDES; do
		for INC in $H_DIRS; do
			if [[ -f "$INC/$H" ]]; then
				includes "$INC/$H"
				printf " $INC/$H"
			fi
		done
	done
};

C_FILES=`find "$C_DIR" -type f -print | grep -E '\.c(pp)?$'`
O_FILES=""
O_LIBS=""
O_DIRS=""

MAX_LEN="${#NAME}"

PHONY=""

function create_c_rule()
{
	if [[ "${#1}" -gt "$MAX_LEN" ]]; then
		MAX_LEN="${#1}"
	fi
	O_FILE=`echo "$1.o" | sed -E 's#^'"$C_DIR"'#'"$O_DIR"'#'`
	O_FILES="$O_FILES $O_FILE"
	printf "$O_FILE: $1"
	#echo " $O_FILE" | sed -E 's#[^/]+$##' | tr -d '\n'
	O_DIRS="$O_DIRS `echo "$O_FILE" | sed -E 's#[^/]+$##' | tr -d '\n'`"
	includes "$1"
	echo
	echo "	@printf \$(MSG_0) \$<"
	echo "	@$CC $FLAGS $HEADS -c -o \$@ \$< || printf \$(MSG_1) \$<"
	echo
};

function create_makefile()
{
	echo "# LOL

NAME = $NAME

all: \$(NAME)
"

	for F in $C_FILES; do
		create_c_rule "$F"
	done

	for M in $LIBS; do
		PHONY="$PHONY $M"
		O_LIBS="$O_LIBS $M"
		echo "$M:"
		echo "	@make -C $M"
		echo
	done

	echo "MSG_0 = '"'\\'"033[0;32m%-${MAX_LEN}.${MAX_LEN}s"'\\'"033[0;0m"'\\'"r'
MSG_1 = '"'\\'"033[0;31m%-${MAX_LEN}.${MAX_LEN}s"'\\'"033[0;0m"'\\'"n'

\$(NAME):$O_DIRS$O_LIBS$O_FILES
	@printf \$(MSG_0) \$@
	@$CC $FLAGS -o \$@ $O_FILES $LINKS && echo || printf \$(MSG_1) \$@

$O_DIR/:
	@mkdir -p \$@ 2> /dev/null || true

$O_DIR/%:
	@mkdir -p \$@ 2> /dev/null || true

clean:
	@rm -f$O_FILES 2> /dev/null || true
	@rmdir -p $O_DIR 2> /dev/null || true

fclean: clean
	@rm -f $NAME 2> /dev/null || true

re: fclean all

.PHONY: all clean fclean re make$PHONY"
};

#
# Main
#

echo "---> Generating Makefile <---"

create_makefile > Makefile && printf "\033[0;32m" || printf "\033[0;31m"

printf "Makefile ready.\033[0;0m\n"
